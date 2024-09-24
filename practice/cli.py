from functions import get_todos, write_todos
import time

now = time.strftime("%b %d-%Y %H:%M:%S")
print("It is now ", now)

while True:
    user_action = input("Type add, show, edit, complete or exit: ")
    user_action = user_action.strip()

    if user_action.startswith('add'):
        todo = user_action[4:]
        todos = get_todos()
        todos.append(todo + '\n')

        write_todos(todos)

    elif user_action.startswith('show'):

        todos = get_todos()

        for index, todo in enumerate(todos):
            todo = todo.strip('\n')
            print(f"{index + 1}.{todo}")

    elif user_action.startswith('edit'):
        try:

            number = int(user_action[5:])

            todos = get_todos()

            index = number - 1
            new_todo = input("Enter new todo: ")
            todos[index] = new_todo + '\n'

            write_todos(todos)

        except ValueError:
            print("Your command is not valid.")
            continue

    elif user_action.startswith('complete'):
        try:
            num = int(user_action[9:])

            todos = get_todos()

            index = num - 1
            todo_to_remove = todos[index].strip('\n')
            todos.pop(index)

            write_todos(todos)

            message = f"todo {todo_to_remove} was removed from list."
            print(message)
        except IndexError:
            print("There is no item with given index number.")
            continue
    elif user_action.startswith('exit'):
        break
    else:
        print("Hey, command is not valid.")
print("Bye!")
