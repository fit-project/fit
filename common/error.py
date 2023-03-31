#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
# 
# Copyright (c) 2022 FIT-Project and others
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
###### 

class ErrorMessage:
    def __init__(self):
        self.TITLES = {
            'acquisition': 'Acquisition is not possible',
            'insert_update_case_info': 'Insert/Update case information is not possible',
            'update_config_info': 'Update config information is not possible',
            'form': 'Load data error',
            'software_installation': 'Software is not installed',
            'capture_packet': 'Capture error',
            'screen_recoder': 'Screen Recoder error',
            'save_web_page': 'Save Web Page',
            'save_mail': 'Save Messages',
            'mrsign_configuration_options': 'MRSign configuration options error',
            'login_error': 'Login error',
            'server_error': 'Server error',
            'verification_failed': 'Verification failed',
            'verification_ok': 'Verification success',
            'pec_verified': 'Verification success',
            'pec_not_verified': 'Verification failed',
            'pec_error': 'Login failed',
            'timestamp': 'Timestamp failed'

        }

        self.MESSAGES = {
            'get_case_info': 'An error occurred during get case info from DB! \nSee bellow for more detail.',
            'get_case_id': 'Case ID not Found \nSee bellow for more detail.',
            'get_configuration': 'An error occurred during get configuration info from DB! \nSee bellow for more detail.',
            'insert_update_case_info': 'An error occurred during insert/update case information on the DB! \nSee bellow for more detail.',
            'update_config_info': 'An error occurred during update config information on the DB! \nSee bellow for more detail.',
            'software_installation': 'The required software would appear not to be installed on this PC! \nSee bellow for more detail.',
            'capture_packet': 'An error occurred during network packets acquisition! \nSee bellow for more detail.',
            'screen_recoder': 'An error occurred during screen recoder acquisition! \nSee bellow for more detail.',
            'save_web_page': 'An error occurred during the execution of save_webpage pywebcopy API',
            'save_mail': 'An error occurred during the execution of save_mailmessages',
            'delete_project_folder': 'An error occurred during the execution of shutil.rmtree method',
            'mrsign_path': 'MRSign seem don\'t installed on this path "{}"\nPlease check the configuration.',
            'mrsign_executable': 'MRSign seem not be an executable file "{}"\nPlease check the installation.',
            'mrsign_hostname_or_port': 'Hostname or port appear not to be configured\nPlease check the configuration.',
            'mrsign_username_or_password': 'Username or password appear not to be configured\nPlease check the configuration.',
            'login_error': 'Wrong login credentials.',
            'server_error': 'Wrong server or IMAP port.',
            'verification_failed': 'Timestamp verification failed.',
            'verification_ok': 'Timestamp has been verified successfully.',
            'pec_verified': 'Verification success',
            'pec_not_verified': 'Verification failed',
            'pec_error': 'Login failed',
            'timestamp_timeout': 'Unable to send the timestamp request. Read time out.'


        }
