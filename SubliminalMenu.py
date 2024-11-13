from tkinter import *
from tkinter import ttk
from tokenize import Double
from pymem import *
from pymem.process import *
from settings import *
import keyboard as kb
from threading import Thread
from time import sleep
import sv_ttk
from threading import Thread
import psutil
class Startup():
    def __init__(self, window_title, width, height):
        #create window
        self.win = Tk()
        xcoord, ycoord = self.center(width, height)
        self.win.geometry(f"{width}x{height}+{xcoord}+{ycoord}")
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", 1)
        self.win.wm_attributes("-alpha", 1)
        sv_ttk.set_theme("dark")

        self.title_label = ttk.Label(self.win, text=window_title, font=('Calibri Bold',12))
        self.title_label.pack()

    def center(self, width, height):
        swidth = self.win.winfo_screenwidth()
        sheight = self.win.winfo_screenheight()
        xcoord = (swidth/2) - (width/2)
        ycoord = (sheight/2) - (height/2)
        return int(xcoord), int(ycoord)
    def update(self):
        self.win.update()
    def close(self):
        self.win.destroy()
    def text(self,input):
        self.title_label.config(text=input)

startup = Startup("Finding Subliminal", 200, 100)
startup.text("Finding Subliminal...")
startup.update()

# GRAB CORERCT PID FROM PROCESS LIST BASED ON VIRTUAL MEMORY ALLOCATED SIZE
subliminal = None
processes = psutil.process_iter()
for process in processes:
    if process.name() == "Subliminal.exe" and process.memory_info().vms > 5000000:
        subliminal = process.pid

if not subliminal:
    startup.text("Game Not Found...")
    startup.update()
    sleep(1)
    startup.close()
    exit()
    
#process hook
mem = Pymem(subliminal)
module = module_from_name(mem.process_handle, "Subliminal.exe").lpBaseOfDll
#Gworld mov rax,[7FF79442C620]

startup.text("Finding Gworld...")
startup.update()

aob_address = pymem.pattern.pattern_scan_all(mem.process_handle,b"\x48\x8B\x05....\x8b\x0e\x4c\x8b\xa0....\x85\xc9\x74.")

if not aob_address:
    startup.text("AOB Scan Failed...")
    startup.update()
    sleep(0.5)
    startup.close()
    exit()

#print(aob_address)
aob_offset = mem.read_int(aob_address + 0x3) + 0x7 #0x3 to index to the 4 bytes where the offest from Subliminal.exe is "...." and then 4 more bytes for end fo instruction
Gworld=aob_address+aob_offset
#print(Gworld)
#Gworld = module + 0x1181C620
#offsets

#toggle trackers
noClip = False

def getPointerAddr(base, offsets):
    addr = mem.read_longlong(base)
    for offset in offsets:
        if offset != offsets[-1]:
            addr = mem.read_longlong(addr + offset)
    addr = addr + offsets[-1]
    return addr

startup.text("Building offsets...")
startup.update()
# calculate addresses on launch. performance improvement
cameraShakeAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0xCFC])
cameraRollAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0xB90])
walkSpeedAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x950])
sprintSpeedAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x944])

gravityScaleAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x330, 0x170])
playerzAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x338,0x200])
#camerazAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x350, 0x2A0,0x270])
canJumpAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x8F8])
movementModeAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x330, 0x201])
collisionAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x338, 0x370])
verticalaccellAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x330, 0x358])

startup.text("Done!")
startup.update()
startup.close()
class ModMenu():
    def __init__(self, window_title, width, height):
        #create window
        self.win = Tk()
        xcoord, ycoord = self.center(width, height)
        self.win.geometry(f"{width}x{height}+{xcoord}+{ycoord}")
        self.win.overrideredirect(True)
        self.win.withdraw()
        self.win.wm_attributes("-topmost", 1)
        self.win.wm_attributes("-alpha", 1)
        self.title_label = ttk.Label(self.win, text=window_title, font=('Calibri Bold',12))
        self.title_label.pack()
        
        #theme
        sv_ttk.set_theme("dark")
        
        #info box
        
        #buttons/interractables
        self.cameraShake_btn = ttk.Button(self.win, text="Toggle Camera Shake", command=self.cameraShake_hack)
        self.cameraShake_btn.place(x=10, y=30)

        self.cameraRoll_btn = ttk.Button(self.win, text="Toggle Camera Roll", command=self.cameraRoll_hack)
        self.cameraRoll_btn.place(x=10,y=70)

        self.cameraRoll_btn = ttk.Button(self.win, text="Toggle NoClip", command=self.noClip_hack)
        self.cameraRoll_btn.place(x=10,y=184)

        self.walkSpeed = ttk.Label(self.win, text = "Walk Speed:", font=('Calibri',12))
        self.walkSpeed.place(x=10,y=113)
        self.enter_speed = ttk.Entry(self.win, width=5, font=('Calibri',12))
        self.enter_speed.insert(0,180)
        self.enter_speed.place(x=95, y=109)
        self.walk_submit = ttk.Button(self.win, text = "Set", command=self.walkSpeed_hack)
        self.walk_submit.place(x=160,y=110)
        self.walk_default = ttk.Button(self.win, text = "Default", command=self.ws_Default)
        self.walk_default.place(x=210,y=110)

        self.runSpeed = ttk.Label(self.win, text = "Run Speed:", font=('Calibri',12))
        self.runSpeed.place(x=10,y=150)
        self.run_enter_speed = ttk.Entry(self.win, width=5, font=('Calibri',12))
        self.run_enter_speed.insert(0,330)
        self.run_enter_speed.place(x=95, y=145)
        self.run_submit = ttk.Button(self.win, text = "Set", command=self.runSpeed_hack)
        self.run_submit.place(x=160,y=146)
        self.walk_default = ttk.Button(self.win, text = "Default", command=self.rs_Default)
        self.walk_default.place(x=210,y=146)

        self.exit_btn = ttk.Button(self.win, text="Exit", command=self.win.destroy)
        self.exit_btn.place(x=390, y=260)

    def cameraShake_hack(self):
        global cameraShakeAddr
        
        if(mem.read_float(cameraShakeAddr) > float(0.0)):
            mem.write_float(cameraShakeAddr, float(0))
        else:
            mem.write_float(cameraShakeAddr, float(0.1))




    def cameraRoll_hack(self):
        if(mem.read_bool(cameraRollAddr)):
            mem.write_bool(cameraRollAddr, False)
        else:
            mem.write_bool(cameraRollAddr, True)

    def walkSpeed_hack(self):
        global walkSpeedAddr
        mem.write_float(walkSpeedAddr, float(self.enter_speed.get()))
   
    def ws_Default(self):
        mem.write_float(walkSpeedAddr, float(175))
        self.enter_speed.delete(0,'end')
        self.enter_speed.insert(0,'175')
   
    def runSpeed_hack(self):
        global sprintSpeedAddr
        mem.write_float(sprintSpeedAddr, float(self.run_enter_speed.get()))

    def rs_Default(self):
        mem.write_float(sprintSpeedAddr, float(375))
        self.run_enter_speed.delete(0,'end')
        self.run_enter_speed.insert(0,'375')

    def noClip_hack(self):
        global noClip
        if (mem.read_float(gravityScaleAddr) > 0):
            noClip = True
            mem.write_float(walkSpeedAddr, float(1000))
            mem.write_bool(canJumpAddr,False)
            mem.write_bytes(collisionAddr, b'\x00',1)
            mem.write_bytes(movementModeAddr, b'\x04',1)
            mem.write_float(gravityScaleAddr, float(-0.025))
            sleep(0.1)
            while(mem.read_double(verticalaccellAddr) < -0.2):
                pass
            mem.write_float(gravityScaleAddr, float(0))
        else:
            noClip = False
            mem.write_float(walkSpeedAddr, float(self.enter_speed.get()))
            mem.write_float(gravityScaleAddr, float(4))
            mem.write_bool(canJumpAddr,True)
            mem.write_bytes(collisionAddr, b'\x03',1)
            mem.write_bytes(movementModeAddr, b'\x01',1)


    def center(self, width, height):
        swidth = self.win.winfo_screenwidth()
        sheight = self.win.winfo_screenheight()
        xcoord = (swidth/2) - (width/2)
        ycoord = (sheight/2) - (height/2)
        return int(xcoord), int(ycoord)


def keybinds(modmenu):
    isopen = False
    while True:
        
        if kb.read_key() == ".":
            if isopen == True:
                modmenu.win.withdraw()
                isopen = False
            else:
                modmenu.win.deiconify()
                isopen = True
                modmenu.win.focus_force()
            sleep(0.5)
        if(noClip):
            if kb.is_pressed("space"):
                mem.write_double(playerzAddr, float(mem.read_double(playerzAddr) + 50))
                #mem.write_double(camerazAddr, float(mem.read_double(camerazAddr) + 50))
            elif kb.is_pressed("shift"):
                mem.write_double(playerzAddr, float(mem.read_double(playerzAddr) - 50))
                #mem.write_double(camerazAddr, float(mem.read_double(camerazAddr) - 50))




modmenu = ModMenu("Subliminal Menu", 450, 300)

keybinds_thread = Thread(target=keybinds, args=(modmenu,))
keybinds_thread.setDaemon(True)
keybinds_thread.start()

modmenu.win.mainloop()
