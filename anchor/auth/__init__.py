#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from .results import AuthDetails, AUTH_FAILED

from pecan import conf

if conf.auth.get('ldap'):
    from . import ldap

if conf.auth.get('keystone'):
    from . import keystone


def validate(user, secret):
    if conf.auth.get('static'):
        if secret == conf.auth['static']['secret'] and user == conf.auth['static']['user']:
            return AuthDetails(username=conf.auth['static']['user'], groups=[])

    if conf.auth.get('ldap'):
        res = ldap.login(user, secret)
        if res is not AUTH_FAILED:
            return res

    if conf.auth.get('keystone'):
        res = keystone.login(secret)
        if res is not AUTH_FAILED:
            return res

    return AUTH_FAILED
