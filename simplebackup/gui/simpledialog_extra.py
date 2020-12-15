"""
Extra dialog boxes to extend the tkinter ones

    ask_combobox: get a user to select a element from a Combobox
"""
from tkinter import LEFT, E, W, messagebox
from tkinter.simpledialog import _QueryDialog
from tkinter.ttk import Combobox, Label


class _QueryListIndex(_QueryDialog):
    def __init__(self, title, prompt, values, **kw):
        self.values = values
        super().__init__(title, prompt, **kw)

    def body(self, master):

        w = Label(master, text=self.prompt, justify=LEFT)
        w.grid(row=0, padx=5, sticky=W)

        self.entry = Combobox(master, name="entry", values=self.values)
        self.entry.grid(row=1, padx=5, sticky=W+E)

        return self.entry

    def validate(self):
        if self.entry.current() == -1:
            messagebox.showwarning(
                "No value selected",
                "No value was selected\nPlease try again",
                parent = self
            )
            return 0
        self.result = self.entry.current()
        return 1

    def getresult(self):
        return self.entry.current()


def ask_combobox(title, prompt, values, **kw):
    """
    gets the selected index of the Combobox from the user

        :param title: the dialog title
        :param prompt: the label text
        :param values: list or tuple of elements to
                       select from the Combobox
        :param **kw: see SimpleDialog class
        :return: index of the selected element
    """
    d = _QueryListIndex(title, prompt, values, **kw)
    return d.result
