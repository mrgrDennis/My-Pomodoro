import kivy
kivy.require('1.11.1')
import time
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.button import Button

import openai

openai.api_key = ""

Builder.load_string('''
<CustomLabel@Label>:
    font_size: 18
    halign: 'center'

<Pomodoro>:
    label: timer_label
    orientation: 'vertical'
    padding: 20
    spacing: 20

    BoxLayout:
        size_hint: 1, 0.2
        CustomLabel:
            text: 'Choose difficulty:'
            size_hint_x: 0.3

        BoxLayout:
            orientation: 'horizontal'
            size_hint_x: 0.7
            spacing: 20

            Button:
                text: 'Simple'
                on_press: root.start_pomodoro('simple')

            Button:
                text: 'Medium'
                on_press: root.start_pomodoro('medium')

            Button:
                text: 'Hard'
                on_press: root.start_pomodoro('hard')

    CustomLabel:
        id: timer_label
        text: 'Press a button to start'

    CustomLabel:
        id: program_label
        text: ''
        size_hint_y: 0.8
        text_size: self.width, None
        valign: 'middle'

''')

class Pomodoro(BoxLayout):
    label = ObjectProperty()

    def generate_quiz_prompt(self, difficulty):
        prompt = f"Hey ChatGPT, can you generate a coding problem that's challenging and suitable for an {difficulty}-level Python programmer? The problem should allow the use of third-party libraries and require me to write the actual code for the solution."
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            temperature=0.9,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        program_description = response.choices[0].text.strip()
        return program_description

    def start_pomodoro(self, difficulty):
        if difficulty == 'select difficulty':
            return
        duration = 60 * (['simple', 'medium', 'hard'].index(difficulty) + 1) * 10
        self.label.text = f"{duration // 60:02d}:{duration % 60:02d}"
        program_description = self.generate_quiz_prompt(difficulty)
        self.ids.program_label.text = program_description
        Clock.schedule_interval(self.update_time, 1)
        self.end_time = time.time() + duration

    def update_time(self, nap):
        remaining = self.end_time - time.time()
        if remaining <= 0:
            self.label.text = "Time's up!"
            self.ids.program_label.text = ""
            return False
        self.label.text = f"{int(remaining // 60):02d}:{int(remaining % 60):02d}"

class PomodoroApp(App):
    def build(self):
        return Pomodoro()

if __name__ == '__main__':
    PomodoroApp().run()
