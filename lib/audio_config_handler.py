# -*- coding: utf-8 -*-
# ********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# Audio Configuration Handler
#
# Copyright (C) 2017 Fernando Moyano <jofemodo@zynthian.org>
#
# ********************************************************************
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
#
# ********************************************************************

import os
import copy
import re
import alsaaudio
import logging
import tornado.web
from lib.zynthian_config_handler import ZynthianConfigHandler
from zyngine.zynthian_engine_alsa_mixer import *

# ------------------------------------------------------------------------------
# Soundcard Presets
# ------------------------------------------------------------------------------
try:
    rpi_version_number = int(os.environ.get('RBPI_VERSION_NUMBER', '4'))
except:
    rpi_version_number = 4
if rpi_version_number == 5:
    default_i2s_bufreq_config = "-r 48000 -p 128 -n 2"
else:
    default_i2s_bufreq_config = "-r 48000 -p 256 -n 2"

soundcard_presets = {
    'V5 ADAC': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dacplusadcpro\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -i 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,Digital Right,ADC Left,ADC Right,ADC Left Input,ADC Right Input,PGA Gain Left,PGA Gain Right'
    },
    'Z2 ADAC': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dacplusadcpro\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -i 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,Digital Right,PGA Gain Left,PGA Gain Right,ADC Left Input,ADC Right Input,ADC Left,ADC Right'
    },
    'ZynADAC': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dacplusadcpro\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -i 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,PGA Gain Left,Digital Right,PGA Gain Right,ADC Left Input,ADC Left,ADC Right Input,ADC Right'
    },
    'HifiBerry DAC8X': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dac8x\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry -r 48000 -p 256 -n 2 -o 8 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'HifiBerry DAC+ ADC PRO': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dacplusadcpro\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -i 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,PGA Gain Left,Digital Right,PGA Gain Right,ADC Left Input,ADC Left,ADC Right Input,ADC Right'
    },
    'HifiBerry DAC+ ADC': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dacplusadc\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -i 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,Digital Right'
    },
    'HifiBerry DAC+': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dacplus\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,Digital Right'
    },
    'HifiBerry DAC+ light': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dac\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,Digital Right'
    },
    'HifiBerry DAC+ RTC': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-dac\ndtoverlay=i2c-rtc,ds130\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,Digital Right'
    },
    'HifiBerry Digi': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-digi\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'HifiBerry Amp': {
        'SOUNDCARD_CONFIG': 'dtoverlay=hifiberry-amp\nforce_eeprom_read=0',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:sndrpihifiberry {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'AlloBoss - Innomaker - PCM5142': {
        'SOUNDCARD_CONFIG': 'dtoverlay=allo-boss-dac-pcm512x-audio',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:BossDAC {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': 'Digital Left,PGA Gain Left,Digital Right,PGA Gain Right,ADC Left Input,ADC Left,ADC Right Input,ADC Right'
    },
    'AudioInjector': {
        'SOUNDCARD_CONFIG': 'dtoverlay=audioinjector-wm8731-audio',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:audioinjectorpi {default_i2s_bufreq_config} -o 2 -i 2 -X raw",
        'SOUNDCARD_MIXER': 'Master Left,Capture Left,Master Right,Capture Right'
    },
    'AudioInjector Isolated': {
        'SOUNDCARD_CONFIG': 'dtoverlay=audioinjector-isolated-soundcard',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:audioinjectoris {default_i2s_bufreq_config} -o 2 -i 2 -X raw",
        'SOUNDCARD_MIXER': 'Master Left,Master Right'
    },
    'AudioInjector Ultra': {
        'SOUNDCARD_CONFIG': 'dtoverlay=audioinjector-ultra',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:audioinjectorul {default_i2s_bufreq_config} -o 2 -i 2 -X raw",
        'SOUNDCARD_MIXER': 'DAC Left,DAC Right,PGA'
    },
    'Fe-Pi Audio': {
        'SOUNDCARD_CONFIG': 'dtoverlay=fe-pi-audio',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:0 {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'IQAudio DAC': {
        'SOUNDCARD_CONFIG': 'dtoverlay=iqaudio-dac',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:IQaudIODAC {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'IQAudio DAC+': {
        'SOUNDCARD_CONFIG': 'dtoverlay=iqaudio-dacplus',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:IQaudIODAC {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'IQAudio Digi': {
        'SOUNDCARD_CONFIG': 'dtoverlay=iqaudio-digi-wm8804-audio',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:0 {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'JustBoom DAC': {
        'SOUNDCARD_CONFIG': 'dtoverlay=justboom-dac',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:0 {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'JustBoom Digi': {
        'SOUNDCARD_CONFIG': 'dtoverlay=justboom-digi',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:0 {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'PiSound': {
        'SOUNDCARD_CONFIG': 'dtoverlay=pisound',
        'JACKD_OPTIONS': f"-P 70 -s -S -d alsa -d hw:pisound {default_i2s_bufreq_config} -o 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'Generic USB device': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': f"-P 70 -s -d alsa -d hw:0 -r 48000 -p 256 -n 2 -X raw",
        'SOUNDCARD_MIXER': ''
    },
    'Behringer UCA222': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:CODEC -r 48000 -p 256 -n 3 -s -S -X raw',
        'SOUNDCARD_MIXER': 'PCM'
    },
    'Behringer UMC404HD': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:U192k -r 48000 -p 256 -n 3 -s -S -X raw',
        'SOUNDCARD_MIXER': 'UMC404HD_192k_Output,Mic'
    },
    'Behringer UMC1820': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:UMC1820 -r 48000 -p 256 -n 2 -s -S -X raw',
        'SOUNDCARD_MIXER': 'UMC1820 Output'
    },
    'Behringer X18XR18': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:X18XR18 -r 48000 -p 256 -n 2 -s -S -X raw',
        'SOUNDCARD_MIXER': ''
    },
    'C-Media Electronics (Unitek Y-247A)': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:Device -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': ''
    },
    'Creative-EMU 0202': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:USB -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': ''
    },
    'Edirol UA1-EX': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:UA1EX -r 48000 -p 1024 -n 2 -S -X raw',
        'SOUNDCARD_MIXER': ''
    },
    'GeneralPlus USB': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:Device -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': 'Speaker Left,Speaker Right,Mic Left,Mic Right,Auto Gain Control'
    },
    'Lexicon Alpha': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:Alpha -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': ''
    },
    'M-Audio M-Track Plus 2': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:Plus -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': 'Mic Left,Mic Right,M-Audio M-Track Plus Left,M-Audio M-Track Plus Right'
    },
    'LogicLink UA0099': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:ICUSBAUDIO7D -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': ''
    },
    'Steinberg UR22 MKII': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:UR22mkII -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': 'Clock_Source_41_Validity'
    },
    'Yamaha VKB-100 Vocaloid': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:Keyboard -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': ''
    },
    'Yeti Microphone': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:Microphone -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': 'Speaker Left,Mic Left,Speaker Right,Mic Right'
    },
    'RBPi Headphones': {
        'SOUNDCARD_CONFIG': 'dtparam=audio=on\naudio_pwm_mode=2',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:#DEVNAME# -r 48000 -p 512 -n 3 -o 2 -X raw',
        'SOUNDCARD_MIXER': 'Headphone'
    },
    'RBPi HDMI': {
        'SOUNDCARD_CONFIG': 'dtparam=audio=on',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:#DEVNAME# -r 48000 -p 512 -n 2 -o 2 -X raw',
        'SOUNDCARD_MIXER': 'HDMI Left,HDMI Right'
    },
    'Dummy device': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -d alsa -d hw:0 -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': ''
    },
    'Custom device': {
        'SOUNDCARD_CONFIG': '',
        'JACKD_OPTIONS': '-P 70 -s -S -d alsa -d hw:0 -r 48000 -p 256 -n 2 -X raw',
        'SOUNDCARD_MIXER': ''
    }
}

try:
    zynthian_engine_alsa_mixer.init_zynapi_instance()
    rbpi_device_name = zynthian_engine_alsa_mixer.zynapi_get_rbpi_device_name()
    logging.info("RBPi Device Name: '{}'".format(rbpi_device_name))
except Exception as err:
    rbpi_device_name = None
    logging.error(err)

if rbpi_device_name == "Headphones":
    soundcard_presets['RBPi Headphones']['JACKD_OPTIONS'] = soundcard_presets['RBPi Headphones']['JACKD_OPTIONS'].replace(
        "#DEVNAME#", "Headphones")
    soundcard_presets['RBPi HDMI']['JACKD_OPTIONS'] = soundcard_presets['RBPi HDMI']['JACKD_OPTIONS'].replace(
        "#DEVNAME#", "b1")
elif rbpi_device_name == "ALSA":
    soundcard_presets['RBPi Headphones']['JACKD_OPTIONS'] = soundcard_presets['RBPi Headphones']['JACKD_OPTIONS'].replace(
        "#DEVNAME#", "ALSA")
    soundcard_presets['RBPi HDMI']['JACKD_OPTIONS'] = soundcard_presets['RBPi HDMI']['JACKD_OPTIONS'].replace(
        "#DEVNAME#", "ALSA")
else:
    del soundcard_presets['RBPi Headphones']
    del soundcard_presets['RBPi HDMI']

# ------------------------------------------------------------------------------
# Audio Configuration Class
# ------------------------------------------------------------------------------


class AudioConfigHandler(ZynthianConfigHandler):

    zctrls = None

    @tornado.web.authenticated
    def get(self, errors=None):

        zc_config = {
            'ZCONTROLLERS': AudioConfigHandler.get_controllers()
        }
        logging.info(zc_config)

        config = {}

        jack_config = os.environ.get('JACKD_OPTIONS', "-P 70 -t 2000 -s -d alsa -d hw:0 -r 48000 -p 256 -n 2")
        device = 'hw:0'
        samplerate = 48000
        num_frames = 1024
        num_periods = 2
        mode_soft = '0'
        mode_16 = '0'
        try:
            alsa_config = re.split('-d\salsa', jack_config)[1]
            alsa_config = f" {alsa_config.strip()} "
            if ' -s ' in alsa_config:
                mode_soft = '1'
                alsa_config.replace(' -s ', ' ')
            if ' -S ' in alsa_config:
                mode_16 = '1'
                alsa_config.replace(' -S ', ' ')
            a_config = re.findall(r"-(\w)\s*([\w:]+)", alsa_config)
            for c in a_config:
                match c[0]:
                    case 'd':
                        device = c[1]
                    case 'r':
                        samplerate = c[1]
                    case 'p':
                        num_frames = c[1]
                    case 'n':
                        num_periods = c[1]
        except Exception as e:
            logging.error(f"Bad jack configuration {e}")
        device = device[3:]
        device_list = []
        for pcm in alsaaudio.pcms():
            if pcm.startswith("hw:CARD="):
                device_list.append(pcm[8:].split(',')[0])

        if os.environ.get('ZYNTHIAN_KIT_VERSION') != 'Custom':
            custom_options_disabled = True
            config['ZYNTHIAN_MESSAGE'] = {
                'type': 'html',
                'content': "<div class='alert alert-warning'>Some config options are disabled. You may want to <a href='/hw-kit'>choose Custom Kit</a> for enabling all options.</div>"
            }
        else:
            custom_options_disabled = False

        scpresets = copy.copy(soundcard_presets)
        if os.environ.get('ZYNTHIAN_DISABLE_RBPI_AUDIO', '0') == '1':
            try:
                del scpresets['RBPi Headphones']
                del scpresets['RBPi HDMI']
            except:
                pass

        config['SOUNDCARD_NAME'] = {
            'type': 'select',
            'title': "Soundcard",
            'value': os.environ.get('SOUNDCARD_NAME'),
            'options': list(scpresets.keys()),
            'presets': scpresets,
            'disabled': custom_options_disabled,
            'refresh_on_change': True
        }
        config['SOUNDCARD_CONFIG'] = {
            'type': 'textarea',
            'title': "Driver Config",
            'cols': 50,
            'rows': 4,
            'value': os.environ.get('SOUNDCARD_CONFIG'),
            'advanced': True,
            'disabled': custom_options_disabled
        }
        config['ALSA_DEVICE'] = {
            'type': 'select',
            'title': "Soundcard Device",
            'value': device,
            'options': device_list,
            'refresh_on_change': True
        }
        config['ALSA_SAMPLERATE'] = {
            'type': 'select',
            'title': "Samplerate",
            'value': str(samplerate),
            'options': ['32000', '44100', '48000', '96000'],
            'refresh_on_change': True
        }
        config['ALSA_NUM_FRAMES'] = {
            'type': 'select',
            'title': "Buffer Size",
            'value': str(num_frames),
            'options': ['64', '128', '256', '512', '1024', '2048'],
            'refresh_on_change': True
        }
        config['ALSA_NUM_PERIODS'] = {
            'type': 'select',
            'title': "Number of Buffers",
            'value': str(num_periods),
            'options': ['2', '3'],
            'refresh_on_change': True
        }
        config['ALSA_MODE_16'] = {
            'type': 'boolean',
            'title': '16-bit',
            'value': mode_16,
            'refresh_on_change': True
        }
        config['ALSA_MODE_SOFT'] = {
            'type': 'boolean',
            'title': 'Soft x-run mode',
            'value': mode_soft,
            'refresh_on_change': True
        }
        config['JACKD_OPTIONS'] = {
            'type': 'text',
            'title': "Jackd Options",
            'value': os.environ.get('JACKD_OPTIONS', "-P 70 -t 2000 -s -d alsa -d hw:0 -r 48000 -p 256 -n 2"),
            'advanced': True,
            'disabled': custom_options_disabled
        }
        config['ZYNTHIAN_AUBIONOTES_OPTIONS'] = {
            'type': 'text',
            'title': "Aubionotes Options",
            'value': os.environ.get('ZYNTHIAN_AUBIONOTES_OPTIONS', "-O complex -t 0.5 -s -88  -p yinfft -l 0.5"),
            'advanced': True
        }
        if rpi_version_number <= 4:
            config['ZYNTHIAN_DISABLE_RBPI_AUDIO'] = {
                'type': 'boolean',
                'title': "Disable RBPi Audio",
                'value': os.environ.get('ZYNTHIAN_DISABLE_RBPI_AUDIO', '0'),
                'advanced': True,
                'refresh_on_change': True
            }
            if os.environ.get('ZYNTHIAN_DISABLE_RBPI_AUDIO', '0') == '0' and os.environ.get('SOUNDCARD_NAME') != "RBPi Headphones":
                config['ZYNTHIAN_RBPI_HEADPHONES'] = {
                    'type': 'boolean',
                    'title': "RBPi Headphones",
                    'value': os.environ.get('ZYNTHIAN_RBPI_HEADPHONES', '0')
                }
        config['SOUNDCARD_MIXER'] = {
            'type': 'textarea',
            'title': "Mixer Controls",
            'value': os.environ.get('SOUNDCARD_MIXER'),
            'cols': 50,
            'rows': 3,
            'addButton': 'display_zcontroller_panel',
            'addPanel': 'zcontroller.html',
            'addPanelConfig': zc_config,
            'advanced': True
        }
        config['_SPACER_'] = {
            'type': 'html',
            'content': "<br>"
        }

        super().get("Audio", config, errors)

    @tornado.web.authenticated
    def post(self):
        self.request.arguments['ZYNTHIAN_DISABLE_RBPI_AUDIO'] = self.request.arguments.get(
            'ZYNTHIAN_DISABLE_RBPI_AUDIO', '0')
        self.request.arguments['ZYNTHIAN_RBPI_HEADPHONES'] = self.request.arguments.get(
            'ZYNTHIAN_RBPI_HEADPHONES', '0')

        device = self.get_argument('ALSA_DEVICE')
        samplerate = self.get_argument('ALSA_SAMPLERATE')
        num_frames = self.get_argument('ALSA_NUM_FRAMES')
        num_periods = self.get_argument('ALSA_NUM_PERIODS')
        jackd_options = self.get_argument('JACKD_OPTIONS', os.environ.get('JACKD_OPTIONS'))

        try:
            jackd_config, alsa_config = re.split('-d\salsa', jackd_options)
            alsa_config = f" {alsa_config.strip()} "
            alsa_config.replace(' -S ', ' ')
            alsa_config.replace(' -s ', ' ')
            a_config = re.findall(r"-(\w)\s*([\w:]+)", alsa_config)
            jackd_options = f"{jackd_config.strip()} -d alsa"
            for c in a_config:
                match c[0]:
                    case 'd':
                        jackd_options += f" -{c[0]} hw:{device}"
                        device = None
                    case 'r':
                        jackd_options += f" -{c[0]} {samplerate}"
                        samplerate = None
                    case 'p':
                        jackd_options += f" -{c[0]} {num_frames}"
                        num_frames = None
                    case 'n':
                        jackd_options += f" -{c[0]} {num_periods}"
                        num_periods = None
                    case _:
                        jackd_options += f" -{c[0]} {c[1]}"
            if device is not None:
                jackd_options += f" -d hw:{device}"
            if samplerate is not None:
                jackd_options += f" -r {samplerate}"
            if num_frames is not None:
                jackd_options += f" -p {num_frames}"
            if num_periods is not None:
                jackd_options += f" -n {num_periods}"
        except Exception as e:
            logging.error(e)
        if self.get_argument('ALSA_MODE_SOFT', '0') == '1':
                jackd_options += " -s"
        if self.get_argument('ALSA_MODE_16', '0') == '1':
            jackd_options += " -S"
        self.request.arguments["JACKD_OPTIONS"] = [jackd_options.encode('utf-8')]

        try:
            previous_soundcard = os.environ.get('SOUNDCARD_NAME')
            current_soundcard = self.get_argument('SOUNDCARD_NAME')
            if current_soundcard.startswith('AudioInjector') and current_soundcard != previous_soundcard:
                self.persist_update_sys_flag()
            if current_soundcard == "RBPi Headphones":
                self.request.arguments['ZYNTHIAN_RBPI_HEADPHONES'] = ['0']
        except:
            pass

        posted_config = tornado.escape.recursive_unicode(
            self.request.arguments)

        command = self.get_argument('_command', '')
        logging.info("COMMAND = {}".format(command))

        if command == 'REFRESH':
            errors = None
            self.config_env(posted_config)
        else:
            for k in list(posted_config):
                if k.startswith('ZYNTHIAN_CONTROLLER') or k.startswith('ALSA_'):
                    del posted_config[k]
            errors = self.update_config(posted_config)
            self.reboot_flag = True

        self.get(errors)

    def get_device_name(self):
        try:
            zynthian_engine_alsa_mixer.init_zynapi_instance()
            device_name = zynthian_engine_alsa_mixer.zynapi_get_device_name()
        except Exception as e:
            device_name = 0
            logging.error(e)

        return device_name

    @classmethod
    def get_controllers(cls):
        try:
            zynthian_engine_alsa_mixer.init_zynapi_instance()
            AudioConfigHandler.zctrls = zynthian_engine_alsa_mixer.zynapi_get_controllers(
                "*")
            return AudioConfigHandler.zctrls
        except Exception as e:
            logging.error(e)
            return []

# ------------------------------------------------------------------------------
