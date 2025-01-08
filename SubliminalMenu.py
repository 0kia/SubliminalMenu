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
import sys

#---------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------

class Startup():
    def __init__(self, window_title, width, height):
        #create window
        self.win = Tk()
        xcoord, ycoord = self.center(width, height)
        self.win.geometry(f"{width}x{height}+{xcoord}+{ycoord}")
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", 1)
        self.win.wm_attributes("-alpha", 1)
        sv_ttk.use_dark_theme()

        self.title_label = ttk.Label(self.win, text=window_title, font=('Calibri Bold',16))
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

#---------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------

class VerticalVelocity():
    def __init__(self, window_title, width, height):
        #create window
        self.win = Tk()
        xcoord, ycoord = self.center(width, height)
        self.win.geometry(f"{width}x{height}+{xcoord}+{ycoord}")
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", 1)
        self.win.wm_attributes("-alpha", 1)
        sv_ttk.use_dark_theme()

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

#---------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------


startup = Startup("Finding Subliminal", 250, 30)
startup.text("Finding Subliminal...")
startup.update()

# GRAB CORERCT PID FROM PROCESS LIST BASED ON VIRTUAL MEMORY ALLOCATED SIZE
subliminal = None
processes = psutil.process_iter()
for process in processes:
    if "Subliminal" in process.name() and process.memory_info().vms > 5000000:
        # if ("Shipping") in process.name():
        #     shipping = True
        subliminal = process.pid
        break

if not subliminal:
    startup.text("Game Not Found...")
    startup.update()
    sleep(1)
    startup.close()
    sys.exit()

#process hook + find module 'Subliminal.exe'
mem = Pymem(subliminal)
module = module_from_name(mem.process_handle, process.name())

startup.text("Finding Gworld...")
startup.update()

#Gworld
aob_address = pymem.pattern.pattern_scan_module(mem.process_handle,module, b"\x48\x8B\x1D....\x48\x85\xDB\x74.\x41\xB0\x01")

print(aob_address)
if not aob_address:
    startup.text("Gworld Not Found...")
    startup.update()
    sleep(1)
    startup.close()
    sys.exit()

#calculate and print(aob_address)
aob_offset = mem.read_int(aob_address + 0x3) + 0x7 #0x3 to index to the 4 bytes where the offest from Subliminal.exe is "...." and then 4 more bytes for end fo instruction
print(aob_offset)

Gworld=aob_address+aob_offset
#print final found Gworld (Gworld)

startup.text("Finding Viewmode...")
startup.update()
# if(shipping):.
viewmode_address = pymem.pattern.pattern_scan_all(mem.process_handle,b"\x00\x00\x00\x00\x00..\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\xFF\xF8")
if not viewmode_address:
    startup.text("ViewMode Not Found...")
    startup.update()
    sleep(1)
    startup.close()
    sys.exit()
viewmode_address = viewmode_address + 0xD
# else: 
#     viewmode_address = pymem.pattern.pattern_scan_all(mem.process_handle,b"\x07\x17\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00")
#     viewmode_address = viewmode_address + 0x8

print(viewmode_address)

startup.text("Building offsets...")
startup.update()

#---------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------

def getPointerAddr(base, offsets):
    addr = mem.read_longlong(base)
    for offset in offsets:
        if offset != offsets[-1]:
            addr = mem.read_longlong(addr + offset)
    addr = addr + offsets[-1]
    return addr

# calculate addresses on launch. performance improvement (based on exe)

cameraShakeAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0xCF4])
cameraRollAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0xB88])
walkSpeedAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x948])
sprintSpeedAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x93C])
FOVAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x370, 0x2BC]) #PlayerCameraManager -> padding after DefaultFOV is LockedFOV (private property)
cursorAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0xC58, 0x348])
#used for noclip
gravityScaleAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x330, 0x170])
playerzAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x338,0x200]) #CapsuleComponent -> somewhere around 200 will be the real cooridanates
canJumpAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x8F0])
movementModeAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x330, 0x201]) #Emovementmode
collisionAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x338, 0x370]) #Acharacter ? -> CapsuleComponent -> Fbodyinstance
verticalaccellAddr = getPointerAddr(Gworld, [0x1E0, 0x38, 0x0, 0x30, 0x300, 0x330, 0x358]) #CharacterMovementComponent -> LastUpdateVelocity.z

#toggle trackers
noClip = False

startup.close()

#---------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------

class ModMenu():
    def __init__(self, window_title, width, height):
        #create window
        self.win = Tk()
        self.xcoord, self.ycoord = self.center(width, height)
        self.win.geometry(f"{width}x{height}+{self.xcoord}+{self.ycoord}")
        self.win.overrideredirect(True)
        self.win.withdraw()
        self.win.wm_attributes("-topmost", 1)
        self.win.wm_attributes("-alpha", 1)
        self.title_label = ttk.Label(self.win, text=window_title, font=('Calibri Bold',12))
        self.title_label.pack()
        
        #theme
        sv_ttk.use_dark_theme()
        
        #info box
        
        #buttons/interractables
        self.cameraShake_btn = ttk.Button(self.win, text="Toggle Camera Shake", command=self.cameraShake_hack)
        self.cameraShake_btn.place(x=10, y=30)

        self.cameraRoll_btn = ttk.Button(self.win, text="Toggle Camera Roll", command=self.cameraRoll_hack)
        self.cameraRoll_btn.place(x=10,y=65)

        self.cameraRoll_btn = ttk.Button(self.win, text="Toggle NoClip", command=self.noClip_hack)
        self.cameraRoll_btn.place(x=190,y=30)

        self.cameraRoll_btn = ttk.Button(self.win, text="Toggle Unlit", command=self.unlit_toggle)
        self.cameraRoll_btn.place(x=190,y=65)

        self.cameraRoll_btn = ttk.Button(self.win, text="Toggle Cursor", command=self.cursor_toggle)
        self.cameraRoll_btn.place(x=315.,y=30)

        self.walkSpeed = ttk.Label(self.win, text = "Walk Speed:", font=('Calibri',12))
        self.walkSpeed.place(x=10,y=115)
        self.enter_speed = ttk.Entry(self.win, width=5, font=('Calibri',12))
        self.enter_speed.insert(0,200)
        self.enter_speed.place(x=95, y=110)
        self.walk_submit = ttk.Button(self.win, text = "Set", command=self.walkSpeed_hack)
        self.walk_submit.place(x=160,y=111)
        self.walk_default = ttk.Button(self.win, text = "Default", command=self.ws_Default)
        self.walk_default.place(x=210,y=111)

        self.runSpeed = ttk.Label(self.win, text = "Run Speed:", font=('Calibri',12))
        self.runSpeed.place(x=10,y=150)
        self.run_enter_speed = ttk.Entry(self.win, width=5, font=('Calibri',12))
        self.run_enter_speed.insert(0,400)
        self.run_enter_speed.place(x=95, y=145)
        self.run_submit = ttk.Button(self.win, text = "Set", command=self.runSpeed_hack)
        self.run_submit.place(x=160,y=146)
        self.run_default = ttk.Button(self.win, text = "Default", command=self.rs_Default)
        self.run_default.place(x=210,y=146)

        self.fovSpeed = ttk.Label(self.win, text = "FOV:", font=('Calibri',12))
        self.fovSpeed.place(x=10,y=185)
        self.fov_enter_speed = ttk.Entry(self.win, width=5, font=('Calibri',12))
        self.fov_enter_speed.insert(0,91)
        self.fov_enter_speed.place(x=95, y=180)
        self.fov_submit = ttk.Button(self.win, text = "Set", command=self.FOV_hack)
        self.fov_submit.place(x=160,y=181)
        self.fov_default = ttk.Button(self.win, text = "Default", command=self.FOV_default)
        self.fov_default.place(x=210,y=181)

        self.exit_btn = ttk.Button(self.win, text="Exit", command=self.win.destroy)
        self.exit_btn.place(x=390, y=260)

    def cursor_toggle(self):
        if(mem.read_double(cursorAddr) > float(0.0)):
            mem.write_double(cursorAddr, float(0))
        else:
            mem.write_double(cursorAddr, float(0.3))

    def cameraShake_hack(self):
        global cameraShakeAddr
        
        if(mem.read_float(cameraShakeAddr) > float(0.0)):
            mem.write_float(cameraShakeAddr, float(0))
        else:
            mem.write_float(cameraShakeAddr, float(1))

    def cameraRoll_hack(self):
        if(mem.read_bool(cameraRollAddr)):
            mem.write_bool(cameraRollAddr, False)
        else:
            mem.write_bool(cameraRollAddr, True)

    def walkSpeed_hack(self):
        global walkSpeedAddr
        mem.write_float(walkSpeedAddr, float(self.enter_speed.get()))
    
    def FOV_hack(self):
        global FOVAddr
        mem.write_float(FOVAddr, float(self.fov_enter_speed.get()))
    
    def FOV_default(self):
        mem.write_float(FOVAddr, float(91))
        self.fov_enter_speed.delete(0, 'end')
        self.fov_enter_speed.insert(0, '91')

    def ws_Default(self):
        mem.write_float(walkSpeedAddr, float(175))
        self.enter_speed.delete(0,'end')
        self.enter_speed.insert(0,'200')
   
    def runSpeed_hack(self):
        global sprintSpeedAddr
        mem.write_float(sprintSpeedAddr, float(self.run_enter_speed.get()))

    def rs_Default(self):
        mem.write_float(sprintSpeedAddr, float(375))
        self.run_enter_speed.delete(0,'end')
        self.run_enter_speed.insert(0,'400')

    def noClip_hack(self):
        global noClip
        Vert = False
        if (mem.read_float(gravityScaleAddr) > 0):
            noClip = True
            mem.write_float(walkSpeedAddr, float(1000))
            mem.write_bool(canJumpAddr,False)
            mem.write_bytes(collisionAddr, b'\x00',1)
            mem.write_bytes(movementModeAddr, b'\x04',1)
            
            #handle giant vertical velocity
            if(mem.read_double(verticalaccellAddr) < -100):
                Vert = True
                handle = VerticalVelocity("offsetting your giant vertical velocity...",300,25)
                handle.update()
                mem.write_float(gravityScaleAddr, float(-2))
                while(mem.read_double(verticalaccellAddr) < -50):
                    pass

            mem.write_float(gravityScaleAddr, float(-0.025))
            sleep(0.1)
            while(mem.read_double(verticalaccellAddr) < -0.2):
                pass
            mem.write_float(gravityScaleAddr, float(0))
            if Vert:
                handle.close()
        else:
            noClip = False
            mem.write_float(walkSpeedAddr, float(self.enter_speed.get()))
            mem.write_float(gravityScaleAddr, float(4))
            mem.write_bool(canJumpAddr,True)
            mem.write_bytes(collisionAddr, b'\x03',1)
            mem.write_bytes(movementModeAddr, b'\x01',1)
        

    def unlit_toggle(self):
        if mem.read_bytes(viewmode_address,1) == b'\x03':
            mem.write_bytes(viewmode_address, b'\x02',1)
        else:
            mem.write_bytes(viewmode_address, b'\x03',1)

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
                modmenu.win.tkraise()
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
