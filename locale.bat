"C:\Program Files (x86)\GnuWin32\bin\xgettext.exe" -L Python -d skirmish smarty.py create.html login.html skirmish.html div_action.html
"C:\Program Files (x86)\GnuWin32\bin\msgmerge.exe" locale/ru/LC_MESSAGES/skirmish.po skirmish.po > locale/ru/LC_MESSAGES/skirmish.po
"C:\Program Files (x86)\GnuWin32\bin\msgfmt.exe" locale/ru/LC_MESSAGES/skirmish.po -o locale/ru/LC_MESSAGES/skirmish.mo