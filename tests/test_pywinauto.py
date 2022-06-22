import pywinauto

# _app = pywinauto.Application().start("c:\\software\\ths\\xiadan.exe")
# wait login window ready
while True:
    try:
        _app = pywinauto.Application().connect(path="c:\\software\\ths\\xiadan.exe", timeout=6)
        print("Connected xiadan.exe")
        login_window_handle = pywinauto.findwindows.find_window(class_name='#32770', found_index=1)
        login_window = _app.window(handle=login_window_handle)
        login_window.Edit1.wait("ready")
        print("Login dialog is ready")
        break
    except Exception as e:

        # print(traceback.format_exc())
        _app = pywinauto.Application().start("c:\\software\\ths\\xiadan.exe", timeout=6)
        print("Start up xiadan.exe")

print("Login Dialog title:", login_window.element_info.name)
login_window.Edit1.set_focus()
login_window.Edit1.type_keys('user')
login_window.Edit2.set_focus()
login_window.Edit2.type_keys('password')
print("Input user & password")
