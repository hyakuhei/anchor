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

from __future__ import absolute_import

from .results import AuthDetails, AUTH_FAILED

import ldap
import ldap.filter
from pecan import conf


def user_get_groups(attributes):
    groups = attributes.get('memberOf', [])
    group_dns = [ldap.dn.explode_dn(g, notypes=True) for g in groups]
    return set(x[0] for x in group_dns if x[1] == 'Groups')


def login(user, secret):
    ldo = ldap.initialize("ldap://%s" % (conf.auth['ldap']['host'],))
    ldo.set_option(ldap.OPT_REFERRALS, 0)
    try:
        ldo.simple_bind_s("%s@%s" % (user, conf.auth['ldap']['domain']), secret)

        filter_str = '(sAMAccountName=%s)' % ldap.filter.escape_filter_chars(user)
        ret = ldo.search_s(conf.auth['ldap']['base'], ldap.SCOPE_SUBTREE,
                           filterstr=filter_str, attrlist=['memberOf'])
        user_attrs = [x for x in ret if x[0] is not None][0][1]
        user_groups = user_get_groups(user_attrs)
        return AuthDetails(username=user, groups=user_groups)
    except ldap.INVALID_CREDENTIALS:
        return AUTH_FAILED
