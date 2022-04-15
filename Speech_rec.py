import os
import speech_recognition as sr
import subprocess
import datetime


class Recognition:
    def __init__(self, file_name, language="ru_RU"):
        self.language = language
        self.file_name = file_name

    def audio_to_text(self, name: str):
        r = sr.Recognizer()
        message = sr.AudioFile(name)
        with message as source:
            audio = r.record(source)
        result = r.recognize_google(audio, language=self.language)
        return result

    def get_audio_messages(self):
        try:
            subprocess.call(
                f'bin/ffmpeg.exe -i {self.file_name} {self.file_name.split(".")[0]}.wav')
            result = self.audio_to_text(self.file_name.split(".")[0] + ".wav")
            return result

        except sr.UnknownValueError:
            '''with open(self.logfile, 'a', encoding='utf-8') as file:
                file.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' +
                           str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' +
                           str(message.from_user.username) + ':' + str(
                    message.from_user.language_code) + ':Message is empty.\n')'''
            return "Ничего не услышал, попробуй еще"

        except Exception as e:
            print(e, "eee")
            '''with open(self.logfile, 'a', encoding='utf-8') as file:
                file.write(str(datetime.datetime.today().strftime("%H:%M:%S")) + ':' + str(message.from_user.id) + ':' +
                           str(message.from_user.first_name) + '_' + str(message.from_user.last_name) + ':' +
                           str(message.from_user.username) + ':' + str(message.from_user.language_code) + ':' + str(
                    e) + '\n')'''
            return "Ой, неизвестная ошибка"

        finally:
            pass
            os.remove(self.file_name)
            os.remove(self.file_name.split(".")[0] + ".wav")

