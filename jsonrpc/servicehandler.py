"""
  Copyright (c) 2012 David Aguilar
  Copyright (c) 2007 Jan-Klaas Kollhof

  This file is part of jsonrpc.

  jsonrpc is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""

from jsonrpc import loads, dumps, JSONEncodeException


def servicemethod(fn):
    fn.jsonrpc_servicemethod = True
    return fn


class ServiceException(Exception):
    pass


class ServiceRequestNotTranslatable(ServiceException):
    pass


class BadServiceRequest(ServiceException):
    pass


class ServiceMethodNotFound(ServiceException):
    def __init__(self, method_name):
        self.method_name = method_name


class ServiceHandler(object):
    def __init__(self, service):
        self.service = service

    def handle_request(self, json):
        err = None
        result = None
        id_ = ''

        try:
            req = self.translate_request(json)
        except ServiceRequestNotTranslatable, e:
            err = e
            req = {'id': id_}

        if err is None:
            try:
                id_ = req['id']
                method = req['method']
                args = req['params']
            except:
                err = BadServiceRequest(json)

        if err is None:
            try:
                meth = self.find_service_method(method)
            except Exception, e:
                err = e

        if err is None:
            try:
                result = self.invokeServiceEndpoint(meth, args)
            except Exception, e:
                err = e

        return self.translate_result(result, err, id_)

    def translate_request(self, data):
        try:
            return loads(data)
        except:
            raise ServiceRequestNotTranslatable(data)

    def find_service_method(self, name):
        try:
            meth = getattr(self.service, name)
            if getattr(meth, 'jsonrpc_servicemethod'):
                return meth
            else:
                raise ServiceMethodNotFound(name)
        except AttributeError:
            raise ServiceMethodNotFound(name)

    def invokeServiceEndpoint(self, meth, args):
        return meth(*args)

    def translate_result(self, rslt, err, id_):
        if err is not None:
            err = {'name': err.__class__.__name__,
                   'message': unicode(err)}
            rslt = None
        try:
            data = dumps({'result': rslt, 'id': id_, 'error':err})
        except JSONEncodeException:
            err = {'name': 'JSONEncodeException',
                   'message': 'Result Object Not Serializable'}
            data = dumps({'result': None, 'id': id_, 'error': err})

        return data