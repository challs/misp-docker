#!/usr/bin/env python3

# Enable linotp plugin configuration
#
# This depends on the following variables:
# MISP_LINOTP_AUTH   - Must be set to '1' enable the plugin
# MISP_LINOTP_REALM  - Realm name in LinOTP to authenticate against. This
#                      should be the name of a valid realm in LinOTP
# LINOTP_BASEURL     - URL to linotp server. Example: http://linotp.local

import os
import re
import sys

def fatal_error(message):
    print("""
        FATAL: LinOTP plugin is active (MISP_LINOTP_AUTH=1) but cannot be automatically enabled
        Either disable the plugin or check your configuration file
        Error message is: {}
        """.format(message))
    sys.exit(1)

def substitute_value(config_string, variable_name, value):
    """
    Replace the value of a given variable name
    """
    find_re = "('{}' => ')[^']*(')".format(variable_name)
    replace_string = r'\1{}\2'.format(value)
    return re.sub(find_re, replace_string, config_string)

def uncomment_line(config_string, text_to_uncomment, is_escaped=False):
    """
    Uncomment a given line in the configuration string

    @param text_to_uncomment The text to find
    @ret New config string containing replacement
    """
    # Escape the text so it does not trigger any re matches
    if not is_escaped:
        escaped_text = re.escape(text_to_uncomment)
    else:
        escaped_text = text_to_uncomment

    search_re = "// ?({})".format(escaped_text)
    return re.sub(search_re, r"\1", config_string)

def update_bootstrap(filename):
    """
    Update bootstrap: uncomment load LinOTPAuth line
    """
    with open(filename) as f:
        config = ''.join(f.readlines())

    config = uncomment_line(config, r"CakePlugin::load('LinOTPAuth')")

    with open(filename, 'w') as f:
        f.write(config)


def update_config(filename):
    with open(filename) as f:
        config = ''.join(f.readlines())

    # Set auth backend to LinOTP
    config = uncomment_line(config, r"'auth'=>array\('LinOTPA[Uu]th\.LinOTP'\)", is_escaped=True)

    # Find commented out linotp section and remove the comments
    head, linotp, tail = re.split(r'/\*\s*((?:(?!\*/).)*?LinOTP.*?)\s*\*/', config, 1, flags=re.DOTALL)

    # Replace configuration variables
    linotp = substitute_value(linotp, 'baseUrl', os.getenv('LINOTP_BASEURL'))
    linotp = substitute_value(linotp, 'realm', os.getenv('MISP_LINOTP_REALM'))

    with open(filename, 'w') as f:
        f.write(head)
        f.write(linotp)
        f.write(tail)

def main():
    if os.getenv("MISP_LINOTP_AUTH") != '1':
        print("LinOTP plugin is not enabled (set MISP_LINOTP_AUTH=1 to enable)")
        sys.exit(0)

    configfile = 'config.php'

    if not os.path.exists(configfile):
        fatal_error("{} not found - please run this script from the config directory".format(config.php))

    baseurl = os.getenv('LINOTP_BASEURL')

    if not baseurl:
        fatal_error("LINOTP_BASEURL is not set")

    realm = os.getenv('MISP_LINOTP_REALM')
    if not realm:
        fatal_error("MISP_LINOTP_REALM is not set")

    update_bootstrap('bootstrap.php')
    update_config(configfile)

    print("LinOTP enabled for use - url={} realm={}".format(baseurl, realm))

if __name__ == '__main__':
    main()
