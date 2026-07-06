#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re

from flask import Blueprint, Response, request
from pymock import Mock

from app.extensions import db
from app.models.mock import MockData, MockProject

blueprint = Blueprint('mock_endpoint', __name__)

mock_js = Mock().mock_js


def _get_json(text):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def _is_key_value_matched(flow_data, key, value, match_type):
    flow_value = str(flow_data.get(key, ''))
    if match_type == 0:
        if value != flow_value:
            return False
    else:
        if not re.search(value, flow_value, re.IGNORECASE):
            return False
    return True


def _is_matched_request_data(mock_data_item, req_json=None):
    if not mock_data_item.request:
        return True
    request_rules = _get_json(mock_data_item.request)
    if not request_rules:
        return True

    flow_data_map = {
        'query': request.args,
        'headers': request.headers,
    }

    for item in request_rules:
        type_ = item.get('type')
        key = item.get('key')
        value = item.get('value')
        match_type = item.get('match_type', 0)

        if type_ == 'json' and req_json:
            from jsonpath import jsonpath
            flow_value = jsonpath(req_json, key)
            if flow_value:
                if not _is_key_value_matched({key: flow_value[0]}, key, value, match_type):
                    return False
        elif type_ == 'GraphQL' and req_json:
            if req_json.get('operationName'):
                query_name = req_json.get('operationName')
            else:
                query_list = re.findall(r'\S+', req_json.get('query', ''), re.IGNORECASE)
                try:
                    query_name = query_list[1].split('(')[0]
                except IndexError:
                    return False
            if not _is_key_value_matched({key: query_name}, key, value, match_type):
                return False
        elif type_ == 'form-data':
            merged = dict(list(request.form.items()) + list(request.files.items()))
            if not _is_key_value_matched(merged, key, value, match_type):
                return False
        elif type_ == 'x-www-form-urlencoded':
            if not _is_key_value_matched(request.form, key, value, match_type):
                return False
        elif type_ in flow_data_map:
            if not _is_key_value_matched(flow_data_map[type_], key, value, match_type):
                return False
        else:
            return False
    return True


@blueprint.route('/mock/<int:project_id>/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def mock_endpoint(project_id, endpoint):
    project = MockProject.query.filter(MockProject.id == project_id, MockProject.status != -1).first()
    if not project:
        return Response(response=json.dumps({'message': 'Project not found'}, ensure_ascii=False),
                        status=404, content_type='application/json')

    method = request.method
    mock_data_list = MockData.query.filter(
        MockData.project_id == project_id,
        MockData.method == method,
        MockData.status == 1
    ).all()

    req_json = _get_json(request.get_data(as_text=True)) if request.data else None

    endpoint_with_slash = '/' + endpoint

    matched_data = None
    for data in mock_data_list:
        if data.match_type == 0:
            if data.url in endpoint_with_slash or data.url in request.url:
                if _is_matched_request_data(data, req_json):
                    matched_data = data
                    break
        else:
            if re.search(data.url, endpoint_with_slash, re.IGNORECASE) or re.search(data.url, request.url, re.IGNORECASE):
                if _is_matched_request_data(data, req_json):
                    matched_data = data
                    break

    if not matched_data:
        return Response(response=json.dumps({'message': 'No matched mock data', 'endpoint': endpoint_with_slash}, ensure_ascii=False),
                        status=404, content_type='application/json')

    content = json.dumps(mock_js(matched_data.response), ensure_ascii=False) if matched_data.response else ''
    content_type = matched_data.content_type or 'application/json'
    headers = mock_js(matched_data.headers) if matched_data.headers else {}

    response_headers = {'Access-Control-Allow-Origin': '*', 'Content-Type': content_type}
    if isinstance(headers, dict):
        response_headers.update(headers)

    return Response(response=content, status=matched_data.code or 200, headers=response_headers)
