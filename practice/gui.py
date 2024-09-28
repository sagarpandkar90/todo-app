import functions

import FreeSimpleGUI as sg

label = sg.Text("Type in a to-do")
input_box = sg.InputText(tooltip="Enter todo", key='todo')
add_button = sg.Button("Add")
window = sg.Window('My To-Do App',
                   layout=[[[label], [input_box, add_button]]],
                   font=('Helvetica', 20))
while True:
    event, value = window.read()

    match event:
        case "Add":
            todos = functions.get_todos()
            new_todos = value['todo'] + '\n'
            todos.append(new_todos)
            functions.write_todos(todos)
        case sg.WINDOW_CLOSED:
            break

window.close()





