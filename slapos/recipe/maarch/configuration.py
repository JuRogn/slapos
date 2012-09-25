##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import ConfigParser
import lxml.etree
import os

from slapos.recipe.librecipe import GenericBaseRecipe

def xpath_set(xml, settings):
    for path, value in settings.iteritems():
        xml.xpath(path)[0].text = value



class Recipe(GenericBaseRecipe):

    def install(self):
        apps_config_xml = self.create_apps_config_xml()
        core_config_xml = self.create_core_config_xml()

        self.update_phpini(php_ini_path=os.path.join(self.options['php_ini_dir'], 'php.ini'))

        # XXX TODO: database schema and initial data
        # XXX TODO: database schema patch for ipv6
        # XXX TODO: document folder
        # XXX TODO: admin password

        # confirm that everything is done, the app will run without further setup
        self.installed_lock()

        return [
                apps_config_xml,
                core_config_xml,
                ]


    def installed_lock(self):
        """\
        Create an empty file to mean the setup is completed
        """
        htdocs = self.options['htdocs']

        with open(os.path.join(htdocs, 'installed.lck'), 'w'):
            pass


    def create_apps_config_xml(self):
        options = self.options

        folder = os.path.join(options['htdocs'], 'apps/maarch_entreprise/xml')
        config_xml_default = os.path.join(folder, 'config.xml.default')
        config_xml = os.path.join(folder, 'config.xml')

        content = open(config_xml_default, 'rb').read()
        xml = lxml.etree.fromstring(content)

        xpath_set(xml, {
            'CONFIG/databaseserver': options['db_host'],
            'CONFIG/databaseserverport': options['db_port'],
            'CONFIG/databasename': options['db_dbname'],
            'CONFIG/databaseuser': options['db_username'],
            'CONFIG/databasepassword': options['db_password'],
            'CONFIG/lang': options['language'],
            })

        with os.fdopen(os.open(config_xml, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600), 'w') as fout:
            fout.write(lxml.etree.tostring(xml, xml_declaration=True, encoding='utf-8').encode('utf-8'))

        return config_xml


    def create_core_config_xml(self):
        options = self.options

        folder = os.path.join(options['htdocs'], 'core/xml')
        config_xml_default = os.path.join(folder, 'config.xml.default')
        config_xml = os.path.join(folder, 'config.xml')

        content = open(config_xml_default, 'rb').read()
        xml = lxml.etree.fromstring(content)

        xpath_set(xml, {
            'CONFIG/defaultlanguage': options['language'],
            })

        with os.fdopen(os.open(config_xml, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600), 'w') as fout:
            fout.write(lxml.etree.tostring(xml, xml_declaration=True, encoding='utf-8').encode('utf-8'))

        return config_xml


    def update_phpini(self, php_ini_path):
        php_ini = ConfigParser.RawConfigParser()
        php_ini.read(php_ini_path)

        php_ini.set('PHP', 'error_reporting', 'E_ALL & ~E_DEPRECATED & ~E_NOTICE')
        php_ini.set('PHP', 'display_errors', 'On')
        php_ini.set('PHP', 'short_open_tag', 'On')
        php_ini.set('PHP', 'magic_quotes_gpc', 'Off')

        with os.fdopen(os.open(php_ini_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600), 'w') as fout:
            php_ini.write(fout)

