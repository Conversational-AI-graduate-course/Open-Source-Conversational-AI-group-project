from abc import ABC

import gradio as gr

class AbstractGUI(ABC):
    pass

class GradioGUI(AbstractGUI):
    def __init__(self):
        super().__init__()
        
        self.gui = gr.Interface(
            fn=self._test_gui_fn,
            inputs={
                "self": self,
                "aching_object": "textbox"
            },
            outputs="text"
        )
        
    def _test_gui_fn(self, aching_object: str):
        return f"We've known each other for so long. Your {aching_object}'s been aching but, you're too shy to say it."
