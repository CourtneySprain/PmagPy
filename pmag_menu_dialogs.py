#!/usr/bin/env pythonw

#--------------------------------------------------------------
# converting magnetometer files to MagIC format
#--------------------------------------------------------------
import wx
import os
import pmag
import subprocess
import wx.grid
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib import pyplot as plt
import pmag_widgets as pw
import thellier_gui_dialogs
import thellier_gui
import ipmag

import threading
print threading.Thread
from threading import Thread


class ImportOrientFile(wx.Frame):

    """ """
    title = "Import orient.txt file"

    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):

        pnl = self.panel

        TEXT = "Import an orient.txt file into your working directory"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---sizer 1 ----                                   
        self.bSizer1 = pw.sampling_particulars(pnl)

        #---sizer 2 ----
        ncn_keys = ['XXXXY', 'XXXX-YY', 'XXXX.YY', 'XXXX[YYY] where YYY is sample designation, enter number of Y', 'sample name=site name', 'site name in site_name column in orient.txt format input file', '[XXXX]YYY where XXXX is the site name, enter number of X']
        self.bSizer2 = pw.select_ncn(pnl, ncn_keys)
        
        #---sizer 3 ----
        self.bSizer3 = pw.select_specimen_ocn(pnl)

        #---sizer 4 ----
        self.bSizer4 = pw.select_declination(pnl)
        
        #---sizer 5 ----
        TEXT = "Hours to SUBTRACT from local time for GMT, default is 0:"
        self.bSizer5 = pw.labeled_text_field(pnl, TEXT)

        #---sizer 6 ----
        # figure out proper formatting for this.  maybe 2 radio buttons?  option1: overwrite option2: update and append.
        TEXT = "Overwrite er_samples.txt file?"
        label1 = "yes, overwrite file in working directory"
        label2 = "no, update existing er_samples file"
        er_samples_file_present = True
        try:
            open(os.path.join(self.WD, "er_samples.txt"), "rU")
        except Exception as ex:
            er_samples_file_present = False
        if er_samples_file_present:
            self.bSizer6 = pw.labeled_yes_or_no(pnl, TEXT, label1, label2)

        #---sizer 7 ---
        label = "Select bedding conventions (if needed)"
        gridsize = (1, 2, 0, 5)
        choices = "averages all bedding poles and uses average for all samples: default is NO", "Don't correct bedding dip with declination -- already correct"
        self.bSizer7 = pw.check_boxes(pnl, gridsize, choices, label)
        #def __init__(self, parent, gridsize, choices, text):


        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        #------
        vbox=wx.BoxSizer(wx.VERTICAL)

        vbox.AddSpacer(10)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer5, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        try:
            vbox.Add(self.bSizer6, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        except AttributeError:
            pass
        vbox.Add(self.bSizer7, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.AddSpacer(10)
        #vbox.Add(wx.StaticLine(pnl), 0, wx.ALL|wx.EXPAND, 5)
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all= wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)
        hbox_all.AddSpacer(20)
        
        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        WD = self.WD
        full_infile = self.bSizer0.return_value()
        ID, infile = os.path.split(full_infile)
        Fsa = infile[:infile.find('.')] + "_er_samples.txt"
        Fsi = infile[:infile.find('.')] + "_er_sites.txt"
        mcd = self.bSizer1.return_value()
        if mcd:
            mcd = "-mcd " + mcd
        ncn = self.bSizer2.return_value()
        ocn = self.bSizer3.return_value()
        dcn = self.bSizer4.return_value()
        gmt = self.bSizer5.return_value() or 0
        try:
            app = self.bSizer6.return_value()
            if app:
                app = "" # overwrite is True
            else:
                app = "-app" # overwrite is False, append instead
        except AttributeError:
            app = ""
        COMMAND = "orientation_magic.py -WD {} -f {} -ncn {} -ocn {} -dcn {} -gmt {} {} {} -ID {} -Fsa {} -Fsi {}".format(WD, infile, ncn, ocn, dcn, gmt, mcd, app, ID, Fsa, Fsi)
        pw.run_command_and_close_window(self, COMMAND, "er_samples.txt\ner_sites.txt")

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("orientation_magic.py -h")


class ImportAzDipFile(wx.Frame):

    title = "Import AzDip format file"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "Import an AzDip format file into your working directory"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---sizer 1 ----
        self.bSizer1 = pw.sampling_particulars(pnl)

        #---sizer 2 ---
        self.bSizer2 = pw.select_ncn(pnl)

        #---sizer 3 ---
        self.bSizer3 = pw.labeled_text_field(pnl, "Location:")

        #---sizer 4 ----
        TEXT = "Overwrite er_samples.txt file?"
        label1 = "yes, overwrite file in working directory"
        label2 = "no, update existing er_samples file"
        er_samples_file_present = True
        try:
            open(os.path.join(self.WD, "er_samples.txt"), "rU")
        except Exception as ex:
            er_samples_file_present = False
        if er_samples_file_present:
            self.bSizer4 = pw.labeled_yes_or_no(pnl, TEXT, label1, label2)

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)


        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        try:
            vbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        except AttributeError:
            pass
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        WD = self.WD
        full_infile = self.bSizer0.return_value()
        infile = os.path.split(full_infile)[1]
        Fsa = WD + infile + "_er_samples.txt"
        mcd = self.bSizer1.return_value()
        if mcd:
            mcd = "-mcd " + mcd
        ncn = self.bSizer2.return_value()
        loc = self.bSizer3.return_value()
        if loc:
            loc = "-loc " + loc
        try:
            app = self.bSizer4.return_value()
            if app:
                app = "" # overwrite is True
            else:
                app = "-app" # overwrite is False, append instead
        except AttributeError:
            app = ""
        COMMAND = "azdip_magic.py -f {} -Fsa {} -ncn {} {} {} {}".format(full_infile, Fsa, ncn, loc, mcd, app)

        pw.run_command_and_close_window(self, COMMAND, Fsa)

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("azdip_magic.py -h")


class ImportODPCoreSummary(wx.Frame):

    title = "Import ODP Core Summary csv file"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "ODP Core Summary csv file"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to copy to working directory"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        WD = self.WD
        full_infile = self.bSizer0.return_value()
        infile = WD + os.path.split(full_infile)[1]
        COMMAND = "cp {} ./".format(full_infile)
        pw.run_command_and_close_window(self, COMMAND, infile)

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        dlg = wx.MessageDialog(self, "Unaltered file will be copied to working directory", "Help", style=wx.OK|wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()


class ImportODPSampleSummary(wx.Frame):

    title = "Import ODP Sample Summary csv file"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "ODP Sample Summary csv file"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        WD = self.WD
        full_infile = self.bSizer0.return_value()
        ID, infile = os.path.split(full_infile)
        Fsa = infile[:infile.find('.')] + "_er_samples.txt"
        COMMAND = "ODP_samples_magic.py -WD {} -f {} -Fsa {} -ID {}".format(WD, infile, Fsa, ID)
        pw.run_command_and_close_window(self, COMMAND, Fsa)

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("ODP_samples_magic.py -h")



class ImportModelLatitude(wx.Frame):

    title = "Import Model Latitude data file"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "Model latitude data"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        infile = os.path.split(self.bSizer0.return_value())[1]
        outfile = os.path.join(self.WD, infile)
        COMMAND = "cp {} {}".format(infile, self.WD)
        pw.run_command_and_close_window(self, COMMAND, outfile)

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        dlg = wx.MessageDialog(self, "Unaltered file will be copied to working directory", "Help", style=wx.OK|wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()



class ImportKly4s(wx.Frame):

    title = "kly4s format"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "kly4s format"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, btn_text="Add kly4s format file", method = self.on_add_file_button)

        #---sizer 1 ---
        self.bSizer1 = pw.choose_file(pnl, btn_text='add AZDIP file (optional)', method = self.on_add_AZDIP_file_button)
        self.bSizer1a = pw.select_specimen_ocn(pnl)
        

        #---sizer 2 ----
        self.bSizer2 = pw.labeled_text_field(pnl)

        #---sizer 3 ---
        self.bSizer3 = pw.specimen_n(pnl)

        #---sizer 4 ---
        self.bSizer4 = pw.select_ncn(pnl)

        #---sizer 5 ---
        self.bSizer5 = pw.select_specimen_ocn(pnl)
        self.bSizer5.select_orientation_convention.SetSelection(2)

        #---sizer 6 ---
        self.bSizer6 = pw.labeled_text_field(pnl, "Location name:")

        #---sizer 7 ---
        self.bSizer7 = pw.labeled_text_field(pnl, "Instrument name (optional):")


        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.bSizer6, flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
        hbox1.Add(self.bSizer7, flag=wx.ALIGN_LEFT)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1a, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer5, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hbox1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        self.hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_all.AddSpacer(20)
        self.hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(self.hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        self.bSizer1a.ShowItems(False)
        self.hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_add_AZDIP_file_button(self,event):
        text = "choose AZDIP file (optional)"
        pw.on_add_file_button(self.bSizer1, self.WD, event, text)


    def on_okButton(self, event):
        WD = self.WD
        full_infile = self.bSizer0.return_value()
        ID, infile = os.path.split(full_infile)
        outfile = infile + ".magic"
        spec_outfile = infile[:infile.find('.')] + "_er_specimens.txt"
        full_azdip_file = self.bSizer1.return_value()
        azdip_file = os.path.split(full_azdip_file)[1]
        if azdip_file:
            azdip_file = "-fad " + azdip_file
        try:
            ocn = "-ocn" + self.bSizer1a.return_value()
        except:
            ocn = ""
        user = self.bSizer2.return_value()
        if user:
            user = "-usr " + user
        n = self.bSizer3.return_value()
        n = "-spc " + str(n)
        ncn = self.bSizer4.return_value()
        #
        loc = self.bSizer6.return_value()
        if loc:
            loc = "-loc " + loc
        ins = self.bSizer7.return_value()
        if ins:
            ins = "-ins " + ins
        COMMAND = "kly4s_magic.py -WD {} -f {} -F {} {} -ncn {} {} {} {} {} {} -ID {} -fsp {}".format(self.WD, infile, outfile, azdip_file, ncn, ocn, user, n, loc, ins, ID, spec_outfile)
        pw.run_command_and_close_window(self, COMMAND, outfile)

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("kly4s_magic.py -h")


class ImportK15(wx.Frame):

    title = "Import K15 format file"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "Import K15 format file"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)


        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---sizer 1 ----
        self.bSizer1 = pw.specimen_n(pnl)

        #---sizer 2 ---
        self.bSizer2 = pw.select_ncn(pnl)

        #---sizer 3 ---
        self.bSizer3 = pw.labeled_text_field(pnl, label="Location name:")

        #---sizer 4 ---
        self.bSizer4 = pw.labeled_text_field(pnl, label="Instrument name (optional):")

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.LEFT, border=5)
        hbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hbox, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        full_infile = self.bSizer0.return_value()
        ID, infile = os.path.split(full_infile)
        outfile = infile + ".magic"
        samp_outfile = infile[:infile.find('.')] + "_er_samples.txt"
        WD = self.WD
        spc = self.bSizer1.return_value()
        ncn = self.bSizer2.return_value()
        loc = self.bSizer3.return_value()
        if loc:
            loc = "-loc " + loc
        ins = self.bSizer4.return_value()
        if ins:
            ins = "-ins " + ins
        aniso_outfile = infile + '_rmag_anisotropy.txt'
        aniso_results_file = infile + '_rmag_results.txt'
        COMMAND = "k15_magic.py -WD {} -f {} -F {} -ncn {} -spc {} {} {} -ID {} -Fsa {} -Fa {} -Fr {}".format(WD, infile, outfile, ncn, spc, loc, ins, ID, samp_outfile, aniso_outfile, aniso_results_file)
        #print COMMAND
        pw.run_command_and_close_window(self, COMMAND, outfile)

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("k15_magic.py -h")


class ImportSufarAscii(wx.Frame):

    title = "Import Sufar Ascii format file"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "Sufar Ascii format file"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---sizer 1 ----
        self.bSizer1 = pw.labeled_text_field(pnl)

        #---sizer 2 ----
        self.bSizer2 = pw.specimen_n(pnl)

        #---sizer 3 ---
        self.bSizer3 = pw.select_ncn(pnl)

        #---sizer 4 ---
        self.bSizer4 = pw.labeled_text_field(pnl, label="Location name:")

        #---sizer 5 ---
        self.bSizer5 = pw.labeled_text_field(pnl, label="Instrument name (optional):")

        #---sizer 6 ---
        TEXT = "Use default mode?"
        label1 = "spinning (default)"
        label2 = "static 15 position mode"
        self.bSizer6 = pw.labeled_yes_or_no(pnl, TEXT, label1, label2)

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.LEFT, border=5)
        hbox.Add(self.bSizer5, flag=wx.ALIGN_LEFT)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hbox, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer6, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #try:
        #    vbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #except AttributeError:
        #    pass
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        WD = self.WD
        full_infile = self.bSizer0.return_value()
        ID, infile = os.path.split(full_infile)
        outfile = infile + ".magic"
        spec_outfile = infile[:infile.find('.')] + "_er_specimens.txt"
        samp_outfile = infile[:infile.find('.')] + "_er_samples.txt"
        site_outfile = infile[:infile.find('.')] + "_er_sites.txt"
        usr = self.bSizer1.return_value()
        if usr:
            usr = "-usr " + usr
        spc = self.bSizer2.return_value()
        ncn = self.bSizer3.return_value()
        loc = self.bSizer4.return_value()
        if loc:
            loc = "-loc " + loc
        ins = self.bSizer5.return_value()
        if ins:
            ins = "-ins " + ins
        k15 = self.bSizer6.return_value()
        if k15:
            k15 = ""
        else:
            k15 = "-k15"
        COMMAND = "SUFAR4-asc_magic.py -WD {} -f {} -F {} {} -spc {} -ncn {} {} {} {} -ID {}".format(WD, infile, outfile, usr, spc, ncn, loc, ins, k15, ID)
        #print COMMAND
        pw.run_command_and_close_window(self, COMMAND, outfile)
        command = 'mv er_specimens.txt {}'.format(spec_outfile)
        print "Renaming er_specimens.txt file: \n", command
        os.system(command)
        command = 'mv er_samples.txt {}'.format(samp_outfile)
        print "Renaming er_samples.txt file: \n", command
        os.system(command)
        command = 'mv er_sites.txt {}'.format(site_outfile)
        print "Renaming er_sites.txt file: \n", command
        os.system(command)

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("SUFAR4-asc_magic.py -h")



class ImportAgmFile(wx.Frame):

    title = "Import single .agm file"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "Micromag agm format file"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---sizer 1 ---
        self.bSizer1 = pw.labeled_text_field(pnl)

        #---sizer 2 ----
        self.bSizer2 = pw.specimen_n(pnl)

        #---sizer 3 ---
        self.bSizer3 = pw.select_ncn(pnl)

        #---sizer 4 ---
        self.bSizer4 = pw.labeled_text_field(pnl, label="Location name:")

        #---sizer 5 ---
        self.bSizer5 = pw.labeled_text_field(pnl, label="Instrument name (optional):")

        #---sizer 6---
        self.bSizer6 = pw.labeled_yes_or_no(pnl, "Units", "CGS units (default)", "SI units")

        #---sizer 7 ---
        self.bSizer7 = pw.check_box(pnl, "backfield curve")

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.LEFT, border=5)
        hbox1.Add(self.bSizer5, flag=wx.ALIGN_LEFT)
        hbox2.Add(self.bSizer6, flag=wx.ALIGN_LEFT|wx.LEFT, border=5)
        hbox2.Add(self.bSizer7, flag=wx.ALIGN_LEFT)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hbox1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        WD = self.WD
        full_infile = self.bSizer0.return_value()
        ID, infile = os.path.split(full_infile)
        outfile = infile + ".magic"
        spec_outfile = infile[:infile.find('.')] + "_er_specimens.txt"
        user = self.bSizer1.return_value()
        if user:
            user = "-usr " + user
        spc = self.bSizer2.return_value()
        ncn = self.bSizer3.return_value()
        loc = self.bSizer4.return_value()
        if loc:
            loc = "-loc " + loc
        ins = self.bSizer5.return_value()
        if ins:
            ins = "-ins " + ins
        units = self.bSizer6.return_value()
        if units:
            units = 'cgs'
        else:
            units = 'SI'
        bak = ''
        if self.bSizer7.return_value():
            bak = "-bak"
        COMMAND = "agm_magic.py -WD {} -ID {} -f {} -F {} -Fsp {} {} -spc {} -ncn {} {} {} -u {} {}".format(WD, ID, infile, outfile, spec_outfile, user, spc, ncn, loc, ins, units, bak)
        pw.run_command_and_close_window(self, COMMAND, outfile)

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("agm_magic.py -h")



class ImportAgmFolder(wx.Frame):

    title = "Import folder of Micromag agm files"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "Folder of agm files"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_dir(pnl, 'add', method = self.on_add_dir_button)

        #---sizer 0a ----
        text = "Note on input directory:\nAll file names must be SPECIMEN_NAME.AGM for hysteresis\nor SPECIMEN_NAME.IRM for backfield (case insensitive)"
        self.bSizer0a = pw.simple_text(pnl, text)

        #---sizer 1 ----
        self.bSizer1 = pw.labeled_text_field(pnl)

        #---sizer 2 ----
        self.bSizer2 = pw.specimen_n(pnl)

        #---sizer 3 ---
        self.bSizer3 = pw.select_ncn(pnl)

        #---sizer 4 ---
        self.bSizer4 = pw.labeled_text_field(pnl, label="Location name:")

        #---sizer 5 ---
        self.bSizer5 = pw.labeled_text_field(pnl, label="Instrument name (optional):")

        #---sizer 6---
        self.bSizer6 = pw.labeled_yes_or_no(pnl, "Units", "CGS units (default)", "SI units")


        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.LEFT, border=5)
        hbox.Add(self.bSizer5, flag=wx.ALIGN_LEFT)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0a, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hbox, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer6, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_dir_button(self,event):
        text = "choose directory of files to convert to MagIC"
        pw.on_add_dir_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        WD = self.WD
        ID = self.bSizer0.return_value()
        files = os.listdir(ID)
        files = [str(f) for f in files if str(f).endswith('.agm') or str(f).endswith('.irm')]
        usr = self.bSizer1.return_value()
        if usr:
            usr = "-usr " + usr
        spc = self.bSizer2.return_value()
        ncn = self.bSizer3.return_value()
        loc = self.bSizer4.return_value()
        if loc:
            loc = "-loc " + loc
        ins = self.bSizer5.return_value()
        if ins:
            ins = "-ins " + ins
        units = self.bSizer5.return_value()
        if units:
            units = 'cgs'
        else:
            units = 'SI'
        # loop through all .agm and .irm files
        for f in files:
            if f.endswith('.irm'):
                bak = "-bak"
            else:
                bak = ""
            outfile = f + ".magic"
            COMMAND = "agm_magic.py -WD {} -ID {} -f {} -F {} {} -spc {} -ncn {} {} {} -u {} {}".format(WD, ID, f, outfile, usr, spc, ncn, loc, ins, units, bak)
            if files.index(f) == (len(files) - 1): # terminate process on last file call
                pw.run_command_and_close_window(self, COMMAND, outfile)
            else:
                pw.run_command(self, COMMAND, outfile)
                

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton(".py -h")


### Analysis and plots

class CustomizeCriteria(wx.Frame):

    title = "Customize Criteria"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "Update your criteria"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        choices = ['Use default criteria', 'Update default criteria', 'Use no criteria', 'Update existing criteria']
        self.bSizer0 = pw.radio_buttons(pnl, choices)

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(hbox, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #try:
        #    vbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #except AttributeError:
        #    pass
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        choice = self.bSizer0.return_value()
        critout = os.path.join(self.WD, 'pmag_criteria.txt')
        if choice == 'Use default criteria' or choice == 'Use no criteria':
            if choice == 'Use default criteria':
                crit_data=pmag.default_criteria(0)
                crit_data,critkeys=pmag.fillkeys(crit_data)
                pmag.magic_write(critout,crit_data,'pmag_criteria')
                # pop up instead of print
                MSG="Default criteria saved in {}/pmag_criteria.txt".format(self.WD)
            elif choice == 'Use no criteria':
                crit_data = pmag.default_criteria(1)
                pmag.magic_write(critout,crit_data,'pmag_criteria')
                MSG="Extremely loose criteria saved in {}/pmag_criteria.txt".format(self.WD)

            dia = wx.MessageDialog(None,caption="Message:", message=MSG ,style=wx.OK|wx.ICON_INFORMATION)
            dia.ShowModal()
            dia.Destroy()
            self.Parent.Raise()
            self.Destroy()
            return
        if choice == "Update existing criteria":
            try:
                crit_data, file_type = pmag.magic_read(os.path.join(self.WD, "pmag_criteria.txt"))
                if file_type != "pmag_criteria":
                    raise Exception
            except Exception as ex:
                print "exception", ex
                MSG = "No pmag_criteria.txt file found in working directory ({})".format(self.WD)
                dia = wx.MessageDialog(None,caption="Message:", message=MSG ,style=wx.OK|wx.ICON_INFORMATION)
                return 0
            default_criteria = pmag.default_criteria(1)[0]
            crit_data = crit_data[0]
            crit_data = dict(default_criteria, **crit_data)
        elif choice == "Update default criteria":
            crit_data = pmag.default_criteria(0)[0]

        frame = wx.Frame(self)
        window = wx.ScrolledWindow(frame)
        self.boxes = pw.large_checkbox_window(window, crit_data, "Update Acceptance Criteria")
        bSizer = wx.BoxSizer(wx.VERTICAL)
        bSizer.Add(self.boxes)

        hboxok = wx.BoxSizer(wx.HORIZONTAL)
        edit_okButton = wx.Button(window, wx.ID_ANY, "&OK")
        edit_cancelButton = wx.Button(window, wx.ID_ANY, '&Cancel')
        hboxok.Add(edit_okButton, 0, wx.ALL, 5)
        hboxok.Add(edit_cancelButton, 0, wx.ALL, 5 )
        window.Bind(wx.EVT_BUTTON, self.on_cancelButton, edit_cancelButton)
        window.Bind(wx.EVT_BUTTON, self.on_edit_okButton, edit_okButton)

        bSizer.Add(hboxok)
        window.SetSizer(bSizer)
        bSizer.Fit(frame)
        window.SetScrollbars(20, 20, 50, 50)
        frame.Centre()
        frame.Show()
 

    def on_edit_okButton(self, event):
        print self.boxes.return_value()
        crit_data = self.boxes.return_value()
        critout = os.path.join(self.WD, '/pmag_criteria.txt')
        pmag.magic_write(critout, crit_data, 'pmag_criteria')
        MSG = "pmag_criteria.txt file has been updated"
        dia = wx.MessageDialog(None,caption="Message:", message=MSG ,style=wx.OK|wx.ICON_INFORMATION)
        dia.ShowModal()
        dia.Destroy()
        self.on_cancelButton(None)

    def on_cancelButton(self, event):
        for child in self.GetChildren():
            child.Destroy()
            #child_window = child.GetWindow()
            #print child_window
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        print "do help button"
        # have a little info thing pop up





def add_thellier_gui_criteria(acceptance_criteria):
    '''criteria used only in thellier gui
    these criteria are not written to pmag_criteria.txt
    '''
    category="thellier_gui"      
    for crit in ['sample_int_n_outlier_check','site_int_n_outlier_check']:
        acceptance_criteria[crit]={} 
        acceptance_criteria[crit]['category']=category
        acceptance_criteria[crit]['criterion_name']=crit
        acceptance_criteria[crit]['value']=-999
        acceptance_criteria[crit]['threshold_type']="low"
        acceptance_criteria[crit]['decimal_points']=0

    for crit in ['sample_int_interval_uT','sample_int_interval_perc',\
    'site_int_interval_uT','site_int_interval_perc',\
    'sample_int_BS_68_uT','sample_int_BS_95_uT','sample_int_BS_68_perc','sample_int_BS_95_perc','specimen_int_max_slope_diff']:
        acceptance_criteria[crit]={} 
        acceptance_criteria[crit]['category']=category
        acceptance_criteria[crit]['criterion_name']=crit
        acceptance_criteria[crit]['value']=-999
        acceptance_criteria[crit]['threshold_type']="high"
        if crit in ['specimen_int_max_slope_diff']:
            acceptance_criteria[crit]['decimal_points']=-999
        else:        
            acceptance_criteria[crit]['decimal_points']=1
        acceptance_criteria[crit]['comments']="thellier_gui_only"

    for crit in ['average_by_sample_or_site','interpreter_method']:
        acceptance_criteria[crit]={} 
        acceptance_criteria[crit]['category']=category
        acceptance_criteria[crit]['criterion_name']=crit
        if crit in ['average_by_sample_or_site']:
            acceptance_criteria[crit]['value']='sample'
        if crit in ['interpreter_method']:
            acceptance_criteria[crit]['value']='stdev_opt'
        acceptance_criteria[crit]['threshold_type']="flag"
        acceptance_criteria[crit]['decimal_points']=-999

    for crit in ['include_nrm']:
        acceptance_criteria[crit]={} 
        acceptance_criteria[crit]['category']=category
        acceptance_criteria[crit]['criterion_name']=crit
        acceptance_criteria[crit]['value']=True
        acceptance_criteria[crit]['threshold_type']="bool"
        acceptance_criteria[crit]['decimal_points']=-999


    # define internal Thellier-GUI definitions:
    #self.average_by_sample_or_site='sample'
    #self.stdev_opt=True
    #self.bs=False
    #self.bs_par=False







class ZeqMagic(wx.Frame):

    title = "Zeq Magic"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "some text"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---sizer 1 ----
        #self.bSizer1 = pw.specimen_n(pnl)

        #---sizer 2 ---
        #self.bSizer2 = pw.select_ncn(pnl)

        #---sizer 3 ---
        #self.bSizer3 = pw.labeled_text_field(pnl, label="Location name:")

        #---sizer 4 ---
        #self.bSizer4 = pw.labeled_text_field(pnl, label="Instrument name (optional):")


        #---sizer 4 ----
        #try:
        #    open(self.WD + "/er_samples.txt", "rU")
        #except Exception as ex:
        #    er_samples_file_present = False
        #if er_samples_file_present:
        #    self.bSizer4 = pw.labeled_yes_or_no(pnl, TEXT, label1, label2)

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        #hbox = wx.BoxSizer(wx.HORIZONTAL)
        #hbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.LEFT, border=5)
        #hbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(hbox, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #try:
        #    vbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #except AttributeError:
        #    pass
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        COMMAND = "zeq_magic.py -WD {}".format(self.WD)
        print COMMAND
        #pw.run_command_and_close_window(self, COMMAND, "er_samples.txt")

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton(".py -h")



EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
        


class PlotThread(Thread):
    """Plot Thread Class."""

    #----------------------------------------------------------------------
    def __init__(self, core_window, plot_function, args, after_function):
        """
        Init Worker Thread Class.
        Takes as arguments a wxpython window, a long running plotting function, its arguments, and a function to call on completion"""
        Thread.__init__(self)
        self.core_window = core_window
        self.plot_function = plot_function
        self.after_function = after_function
        self.args = args
        self.start()    # start the thread
    
    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        fig, figname = self.plot_function(*self.args)
        if fig:
            del self.core_window.wait
            self.core_window.Destroy()
            dpi = fig.get_dpi()
            pixel_width = dpi * fig.get_figwidth()
            pixel_height = dpi * fig.get_figheight()
            # this one works (but sometimes crashes):
            #wx.CallAfter(self.after_function, (pixel_width, pixel_height+50), fig, figname)
            # this one doesn't work:
            #wx.CallLater(100, self.after_function, (pixel_width, pixel_height+50), fig, figname)
            # trying this one:
            print 'core_window:', self.core_window, 'resultevent', ResultEvent
            wx.PostEvent(self.core_window, ResultEvent(None))
        else:
            pw.simple_warning("No data points met your criteria - try again\nError message: {}".format(figname))
            self.core_window.okButton.Enable()


        

class Core_depthplot(wx.Frame):

    title = "Remanence data vs. depth/height/age"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.wait = None
        self.InitUI()

    def InitUI(self):

        pnl = self.panel
        TEXT = "This program allows you to plot various measurement data versus sample depth.\nYou must provide either a magic_measurements file or a pmag_specimens file (or, you can use both)."
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        EVT_RESULT(self, self.do_thing)
        
        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, btn_text='add measurements file', method = self.on_add_measurements_button, remove_button="Don't use measurements file")

        meas_file = os.path.join(self.WD, 'magic_measurements.txt')
        self.check_and_add_file(meas_file, self.bSizer0.file_path)


        #---sizer 4 ---
        color_choices = ['blue', 'green','red','cyan','magenta', 'yellow', 'black','white']
        self.bSizer4 = pw.radio_buttons(pnl, color_choices, "choose color for plot points")

        #---sizer 5 ---
        shape_choices = ['circle', 'triangle_down','triangle_up','square', 'star','hexagon','+','x','diamond']
        shape_symbols =['o', 'v', '^', 's', '*', 'h', '+', 'x', 'd']
        self.shape_choices_dict = dict(zip(shape_choices, shape_symbols))
        self.bSizer5 = pw.radio_buttons(pnl, shape_choices, "choose shape for plot points")

        #---sizer 5a---
        #self.bSizer5a = pw.labeled_text_field(pnl, "point size (default is 5)")
        self.bSizer5a = pw.labeled_spin_ctrl(pnl, "point size (default is 5): ")
        self.bSizer5b = pw.check_box(pnl, "Show lines connecting points")
        self.bSizer5b.cb.SetValue(True)

        self.Bind(wx.EVT_TEXT, self.change_file_path, self.bSizer0.file_path)


        #---sizer 0a---
        self.bSizer0a = pw.choose_file(pnl, btn_text='add pmag_specimens file', method = self.on_add_pmag_specimens_button, remove_button="Don't use pmag specimens file")
        pmag_spec_file = os.path.join(self.WD, 'pmag_specimens.txt')
        self.check_and_add_file(pmag_spec_file, self.bSizer0a.file_path)

        #--- plotting stuff for pmag_specimens
        self.bSizer0a1 = pw.radio_buttons(pnl, color_choices, "choose color for plot points")

        # set default color to red
        self.bSizer0a1.radio_buttons[2].SetValue(True)
        
        self.bSizer0a2 = pw.radio_buttons(pnl, shape_choices, "choose shape for plot points")

        # set default symbol:
        self.bSizer0a2.radio_buttons[2].SetValue(True)
        
        self.bSizer0a3 = pw.labeled_spin_ctrl(pnl, "point size (default is 5): ")
        
        self.Bind(wx.EVT_TEXT, self.change_results_path, self.bSizer0a.file_path)

        
        #---sizer 1 ---
        self.bSizer1a = pw.labeled_yes_or_no(pnl, "Choose file to provide sample data", "er_samples", "er_ages")
        self.Bind(wx.EVT_RADIOBUTTON, self.on_sample_or_age, self.bSizer1a.rb1)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_sample_or_age, self.bSizer1a.rb2)
        
        self.bSizer1 = pw.choose_file(pnl, btn_text='add er_samples file', method = self.on_add_samples_button)
        sampfile = os.path.join(self.WD, 'er_samples.txt')
        self.check_and_add_file(sampfile, self.bSizer1.file_path)

        #---sizer 2 ----
        self.bSizer2 = pw.choose_file(pnl, btn_text='add IODP core summary csv file (optional)', method = self.on_add_csv_button)
        
        #---sizer 3 ---
        plot_choices = ['Plot declination', 'Plot inclination', 'Plot magnetization', 'Plot magnetization on log scale']
        self.bSizer3 = pw.check_boxes(pnl, (5, 1, 0, 0), plot_choices, "Choose what to plot:")
        self.bSizer3.boxes[0].SetValue(True)
        self.bSizer3.boxes[1].SetValue(True)
        self.bSizer3.boxes[2].SetValue(True)
        self.bSizer3.boxes[3].SetValue(True)


        #---sizer 13---
        protocol_choices = ['AF', 'T', 'ARM', 'IRM']#, 'X'] not supporting susceptibility at the moment
        self.bSizer13 = pw.radio_buttons(pnl, protocol_choices, "Lab Protocol:  ", orientation=wx.HORIZONTAL)

        self.bSizer14 = pw.labeled_text_field(pnl, "Step:  ")

        #self.bSizer15 = pw.check_box(pnl, "Do not plot blanket treatment data")

        self.bSizer16 = pw.radio_buttons(pnl, ['svg', 'eps', 'pdf', 'png'], "Save plot in this format:")

        #---sizer 8 ---
        self.bSizer8 = pw.labeled_yes_or_no(pnl, "Depth scale", "Meters below sea floor (mbsf)", "Meters composite depth (mcd)")


        #---sizer 6 ---
        self.bSizer6 = pw.labeled_text_field(pnl, label="minimum depth to plot (in meters)")

        #---sizer  7---
        self.bSizer7 = pw.labeled_text_field(pnl, label="maximum depth to plot (in meters)")

        #---sizer 9 ---
        self.bSizer9 = pw.check_box(pnl, "Plot GPTS?")
        self.Bind(wx.EVT_CHECKBOX, self.on_checkbox, self.bSizer9.cb)

        # if plotting GPTS, these sizers will be shown:
        self.bSizer10 = pw.labeled_yes_or_no(pnl, "Time scale", "gts04", "ck95")

        self.bSizer11 = pw.labeled_text_field(pnl, label="Minimum age (in Ma)")

        self.bSizer12 = pw.labeled_text_field(pnl, label="Maximum age (in Ma)")

        
        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        #---make all the smaller container boxes---
        vbox = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.StaticBox(pnl)
        box2 = wx.StaticBox(pnl)
        box3 = wx.StaticBox(pnl)
        box4 = wx.StaticBox(pnl)
        box5 = wx.StaticBox(pnl)
        self.vbox1 = wx.StaticBoxSizer(box1, wx.VERTICAL)
        vbox2 = wx.StaticBoxSizer(box2, wx.VERTICAL)
        vbox3 = wx.StaticBoxSizer(box3, wx.VERTICAL)
        vbox4 = wx.StaticBoxSizer(box4, wx.VERTICAL)
        self.vbox5 = wx.StaticBoxSizer(box5, wx.VERTICAL)
        mini_vbox = wx.BoxSizer(wx.VERTICAL)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        #---Plot type and format ---
        hbox0.AddMany([self.bSizer3, self.bSizer16])

        #---Plot display options---
        mini_vbox.AddMany([self.bSizer5a, self.bSizer5b])
        hbox1.Add(self.bSizer4)
        hbox1.Add(self.bSizer5, flag=wx.ALIGN_LEFT)
        hbox1.Add(mini_vbox, flag=wx.ALIGN_LEFT)
        self.vbox1.Add(wx.StaticText(pnl, label="Plot display options for measurements data"))
        self.vbox1.Add(hbox1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)

        # more plot display options

        hbox5.AddMany([self.bSizer0a1, self.bSizer0a2, self.bSizer0a3])
        self.vbox5.Add(wx.StaticText(pnl, label="Plot display options for specimens data"))
        self.vbox5.Add(hbox5)


        #---depths to plot ---
        hbox2.Add(self.bSizer6, flag=wx.ALIGN_LEFT)#|wx.LEFT, border=5)
        hbox2.Add(self.bSizer7, flag=wx.ALIGN_LEFT)
        vbox2.Add(wx.StaticText(pnl, label="Specify depths to plot (optional)"))
        vbox2.Add(hbox2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)


        #---time scale ----
        hbox3.Add(self.bSizer9, flag=wx.ALIGN_LEFT)
        hbox3.Add(self.bSizer10, flag=wx.ALIGN_LEFT)#|wx.LEFT, border=5)
        hbox3.Add(self.bSizer11, flag=wx.ALIGN_LEFT)
        hbox3.Add(self.bSizer12, flag=wx.ALIGN_LEFT)
        vbox3.Add(wx.StaticText(pnl, label="Specify time scale to plot (optional)"))
        vbox3.Add(hbox3)


        #---experiment type and step
        hbox4.Add(self.bSizer13, flag=wx.ALIGN_LEFT)
        hbox4.Add(self.bSizer14, flag=wx.ALIGN_LEFT)
        vbox4.Add(wx.StaticText(pnl, label="Experiment type"))
        vbox4.Add(hbox4)
        #vbox4.Add(self.bSizer15)


        #---add all widgets to main container---
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.vbox1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        
        vbox.Add(self.bSizer0a, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.vbox5, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        
        vbox.Add(self.bSizer1a, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hbox0)

        vbox.Add(vbox4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer8, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(vbox2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(vbox3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)

        #--- add buttons ---
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        self.hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_all.AddSpacer(20)
        self.hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(self.hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)

        
        # hide plotting stuff
        # no longer hiding this initially -- it causes a sizing nightmare
        #if not self.bSizer0.file_path.GetValue():
            #self.vbox1.ShowItems(False)

        #if not self.bSizer0a.file_path.GetValue():
            #self.vbox5.ShowItems(False)


        self.hbox_all.Fit(self)

        # hide gpts stuff
        self.bSizer10.ShowItems(False)
        self.bSizer11.ShowItems(False)
        self.bSizer12.ShowItems(False)
        self.Show()
        self.Centre()

    def do_thing(self):
        print 'doing the thing!!'
        
    def change_results_path(self, event):
        txt_ctrl = event.GetEventObject()
        if txt_ctrl.GetValue():
            self.vbox5.ShowItems(True)
            self.panel.Layout() # resizes scrolled window
            #self.hbox_all.Fit(self) # resizes entire frame
        else:
            self.vbox5.ShowItems(False)
            self.panel.Layout()

    def change_file_path(self, event):
        txt_ctrl = event.GetEventObject()
        if txt_ctrl.GetValue():
            self.vbox1.ShowItems(True)
            self.panel.Layout() # resizes scrolled window
            #self.hbox_all.Fit(self) # resizes entire frame

        else:
            self.vbox1.ShowItems(False)
            self.panel.Layout()


    def on_add_measurements_button(self, event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_add_pmag_specimens_button(self, event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0a, self.WD, event, text)

    def on_sample_or_age(self, event):
        if event.GetId() == self.bSizer1a.rb1.GetId():
            self.bSizer1.add_file_button.SetLabel('add er_samples_file')
            self.check_and_add_file(os.path.join(self.WD, 'er_samples.txt'), self.bSizer1.file_path)
        else:
            self.bSizer1.add_file_button.SetLabel('add er_ages_file')
            self.check_and_add_file(os.path.join(self.WD, 'er_ages.txt'), self.bSizer1.file_path)

    def check_and_add_file(self, infile, add_here):
        if os.path.isfile(infile):
            add_here.SetValue(infile)

    def on_add_samples_button(self, event):
        text = "provide er_samples/er_ages file"
        pw.on_add_file_button(self.bSizer1, self.WD, event, text)

    def on_add_csv_button(self, event):
        text = "provide csv file (optional)"
        pw.on_add_file_button(self.bSizer2, self.WD, event, text)

    def on_checkbox(self, event):
        if event.Checked():
            self.bSizer10.ShowItems(True)
            self.bSizer11.ShowItems(True)
            self.bSizer12.ShowItems(True)
        else:
            self.bSizer10.ShowItems(False)
            self.bSizer11.ShowItems(False)
            self.bSizer12.ShowItems(False)
        self.panel.Layout()
        #self.hbox_all.Fit(self)

    def make_plot_frame(self, (pixel_width, pixel_height), fig, figname):
        PlotFrame((pixel_width, pixel_height), fig, figname)
        
    def on_okButton(self, event):
        """
        get required variables from the interface, then call a worker thread to do the computations.
        """
        meas_file = self.bSizer0.return_value()
        if meas_file:
            meas_file = os.path.split(meas_file)[1]
        pmag_spec_file = self.bSizer0a.return_value()
        if pmag_spec_file:
            pmag_spec_file = os.path.split(pmag_spec_file)[1]
        spec_sym, spec_sym_shape, spec_sym_color, spec_sym_size = "", "", "", ""

        if pmag_spec_file:
            # get symbol/size for dots
            spec_sym_shape = self.shape_choices_dict[self.bSizer0a2.return_value()]
            spec_sym_color = self.bSizer0a1.return_value()[0]
            spec_sym_size = self.bSizer0a3.return_value()
            spec_sym = str(spec_sym_color) + str(spec_sym_shape)
    
        use_sampfile = self.bSizer1a.return_value()
        if use_sampfile:
            samp_file = os.path.split(str(self.bSizer1.return_value()))[1]
            age_file = ''
        else:
            samp_file = ''
            age_file = os.path.split(self.bSizer1.return_value())[1]
        depth_scale = self.bSizer8.return_value()
        if age_file:
            depth_scale='age'
        elif depth_scale:
            depth_scale = 'sample_core_depth' #'mbsf'
        else:
            depth_scale = 'sample_composite_depth' #'mcd'
        dmin = self.bSizer6.return_value()
        dmax = self.bSizer7.return_value()
        if self.bSizer9.return_value(): # if plot GPTS is checked
            pltTime = 1
            if self.bSizer10.return_value():
                timescale = 'gts04'
            else:
                timescale = 'ck95'
            amin = self.bSizer11.return_value()
            amax = self.bSizer12.return_value()
            if not amin or not amax:
                pw.simple_warning("If plotting timescale, you must provide both a lower and an upper bound.\nIf you don't want to plot timescale, uncheck the 'Plot GPTS' checkbox")
                return False
        else: # if plot GPTS is not checked
            pltTime, timescale, amin, amax = 0, '', -1, -1
        sym_shape = self.shape_choices_dict[self.bSizer5.return_value()]
        sym_color = self.bSizer4.return_value()[0]
        sym = sym_color + sym_shape
        size = self.bSizer5a.return_value()
        pltLine = self.bSizer5b.return_value()
        if pltLine:
            pltLine = 1
        else:
            pltLine = 0
        method = str(self.bSizer13.return_value())
        step = self.bSizer14.return_value()
        if not step:
            #-LP [AF,T,ARM,IRM, X] step [in mT,C,mT,mT, mass/vol] to plot
            units_dict = {'AF': 'millitesla', 'T': 'degrees C', 'ARM': 'millitesla', 'IRM': 'millitesla', 'X': 'mass/vol'}
            unit = units_dict[method]
            pw.simple_warning("You must provide the experiment step in {}".format(unit))
            return False
        pltDec, pltInc, pltMag, logit = 0, 0, 0, 0
        for val in self.bSizer3.return_value():
            if 'declination' in val:
                pltDec = 1
            if 'inclination' in val:
                pltInc = 1
            if 'magnetization' in val:
                pltMag = 1
            if 'log' in val:
                logit = 1

        
        fmt = self.bSizer16.return_value()

        # for use as module:

        self.okButton.Disable()
        self.wait = wx.BusyInfo("Please wait, generating plot...")
        #self.wait = wx.ProgressDialog('Plotting', 'Please wait, generating plot', style=wx.PD_CAN_ABORT)
        
        args = [self.WD, meas_file, pmag_spec_file, samp_file, age_file, depth_scale, dmin, dmax, sym, size, spec_sym, spec_sym_size, method, step, fmt, pltDec, pltInc, pltMag, pltLine, 1, logit, pltTime, timescale, amin, amax]
        PlotThread(self, ipmag.core_depthplot, args, self.make_plot_frame)

        
        #fig, figname = ipmag.core_depthplot(self.WD, meas_file, pmag_spec_file, samp_file, age_file, depth_scale, dmin, dmax, sym, size, spec_sym, spec_sym_size, method, step, fmt, pltDec, pltInc, pltMag, pltLine, 1, logit, pltTime, timescale, amin, amax)
        #if fig:
        #    self.Destroy()
        #    dpi = fig.get_dpi()
        #    pixel_width = dpi * fig.get_figwidth()
        #    pixel_height = dpi * fig.get_figheight()
        #    plot_frame = PlotFrame((pixel_width, pixel_height + 50), fig, figname)
        #else:
        #    pw.simple_warning("No data points met your criteria - try again\nError message: {}".format(figname))
        #    self.okButton.Enable()
            
        # for use as command_line:
        if meas_file:
            meas_file = os.path.split(meas_file)[1]
        meas_file = pmag.add_flag(meas_file, '-f')
        if pmag_spec_file:
            pmag_spec_file = os.path.split(pmag_spec_file)[1]
        pmag_spec_file = pmag.add_flag(pmag_spec_file, '-fsp')
        pmag_spec_file = pmag_spec_file + ' ' + spec_sym_color + spec_sym_shape + ' ' + str(spec_sym_size)
        sym = '-sym ' + sym + ' ' + str(size)
        if samp_file:
            samp_file = os.path.split(samp_file)[1]
        samp_file = pmag.add_flag(samp_file, '-fsa')
        if age_file:
            age_file = os.path.split(age_file)[1]
        age_file = pmag.add_flag(age_file, '-fa')
        depth_scale = pmag.add_flag(depth_scale, '-ds')
        depth_range = ''
        if dmin and dmax:
            depth_range = '-d ' + str(dmin) + ' ' + str(dmax)
        if pltTime and amin and amax:
            timescale = '-ts ' + timescale + ' ' + str(amin) + ' ' + str(amax)
        else:
            timescale = ''
        method = pmag.add_flag(method, '-LP') + ' ' + str(step)
        #if not pltSus:
        #    pltSus = "-L"
        #else:
        #    pltSus = ''
        if not pltDec:
            pltDec = "-D"
        else:
            pltDec = ''
        if not pltInc:
            pltInc = "-I"
        else:
            pltInc = ''
        if not pltMag:
            pltMag = "-M"
        else:
            pltMag = ''
        if pltLine:
            pltLine = ""
        else:
            pltLine = '-L' # suppress line
        if logit:
            logit = "-log"
        else:
            logit = ''
        fmt = pmag.add_flag(fmt, '-fmt')

        COMMAND = "core_depthplot.py {meas_file} {pmag_spec_file} {sym} {samp_file} {age_file} {depth_scale} {depth_range} {timescale} {method} {pltDec} {pltInc} {pltMag} {logit} {fmt} {pltLine} -WD {WD}".format(meas_file=meas_file, pmag_spec_file=pmag_spec_file, sym=sym, samp_file=samp_file, age_file=age_file, depth_scale=depth_scale, depth_range=depth_range, timescale=timescale, method=method, pltDec=pltDec, pltInc=pltInc, pltMag=pltMag, logit=logit, fmt=fmt, pltLine=pltLine, WD=self.WD)
        print 'running equivalent to:', COMMAND
        #os.system(COMMAND)


        """
        haven't done these options yet
        wt_file (also sets norm)# -n specimen_filename
        spc_file, spc_sym, spc_size # -fsp spec_file symbol_shape symbol_size
        res_file, res_sym, res_size # -fres pmag_results_file symbol_shape symbol_size
        wig_file (also sets pcol, width) # -fwig wiggle_file(???)
        sum_file # -fsum IODP_core_summary_csv_file

        (sets plots & verbose) # -sav
        """
        
        #pw.run_command_and_close_window(self, COMMAND, "er_samples.txt")

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("core_depthplot.py -h")

        

class Ani_depthplot(wx.Frame):

    title = "Plot anisotropoy vs. depth/height/age"
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.wait = None
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "Anisotropy data can be plotted versus depth.\nThe program ANI_depthplot.py uses MagIC formatted data tables of the rmag_anisotropy.txt and er_samples.txt types.\nrmag_anisotropy.txt stores the tensor elements and measurement meta-data while er_samples.txt stores the depths, location and other information.\nBulk susceptibility measurements can also be plotted if they are available in a magic_measurements.txt formatted file."
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, btn_text='add rmag_anisotropy file', method = self.on_add_rmag_button, remove_button='remove rmag_anisotropy file')
        self.check_and_add_file(os.path.join(self.WD, 'rmag_anisotropy.txt'), self.bSizer0.file_path)

        #---sizer 1 ----
        self.bSizer1 = pw.choose_file(pnl, btn_text='add magic_measurements file', method = self.on_add_measurements_button, remove_button='remove magic_measurements file')
        self.check_and_add_file(os.path.join(self.WD, 'magic_measurements.txt'), self.bSizer1.file_path)

        #---sizer 2 ---
        self.bSizer2a = pw.labeled_yes_or_no(pnl, "Choose file to provide sample data", "er_samples", "er_ages")
        self.Bind(wx.EVT_RADIOBUTTON, self.on_sample_or_age, self.bSizer2a.rb1)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_sample_or_age, self.bSizer2a.rb2)
        
        self.bSizer2 = pw.choose_file(pnl, btn_text='add er_samples file', method = self.on_add_samples_button)
        sampfile = os.path.join(self.WD, 'er_samples.txt')
        self.check_and_add_file(sampfile, self.bSizer2.file_path)

        #---sizer 3---
        self.bSizer3 = pw.radio_buttons(pnl, ['svg', 'eps', 'pdf', 'png'], "Save plot in this format:")
        
        #---sizer 4 ---
        self.bSizer4 = pw.labeled_yes_or_no(pnl, "Depth scale", "Meters below sea floor (mbsf)", "Meters composite depth (mcd)")

        #---sizer 5 ---
        self.bSizer5 = pw.labeled_text_field(pnl, label="minimum depth to plot (in meters)")

        #---sizer  6---
        self.bSizer6 = pw.labeled_text_field(pnl, label="maximum depth to plot (in meters)")

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2a, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.AddMany([self.bSizer5, self.bSizer6])
        vbox.Add(hbox1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_rmag_button(self,event):
        text = "choose rmag_anisotropy file"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)
    
    def on_add_measurements_button(self,event):
        text = "choose magic_measurements file"
        pw.on_add_file_button(self.bSizer1, self.WD, event, text)

    def on_add_samples_button(self, event):
        text = "provide er_samples/er_ages file"
        pw.on_add_file_button(self.bSizer2, self.WD, event, text)

    def on_sample_or_age(self, event):
        if event.GetId() == self.bSizer2a.rb1.GetId():
            self.bSizer2.add_file_button.SetLabel('add er_samples_file')
            self.check_and_add_file(os.path.join(self.WD, 'er_samples.txt'), self.bSizer2.file_path)
        else:
            self.bSizer2.add_file_button.SetLabel('add er_ages_file')
            self.check_and_add_file(os.path.join(self.WD, 'er_ages.txt'), self.bSizer2.file_path)

    def check_and_add_file(self, infile, add_here):
        if os.path.isfile(infile):
            add_here.SetValue(infile)

    def make_plot_frame(self, (pixel_width, pixel_height), fig, figname):
        PlotFrame((pixel_width, pixel_height), fig, figname)
            
    def on_okButton(self, event):
        ani_file = self.bSizer0.return_value()
        meas_file = self.bSizer1.return_value()
        use_sampfile = self.bSizer2a.return_value()
        samp_file, age_file = None, None
        if use_sampfile:
            samp_file = self.bSizer2.return_value()
        else:
            age_file = self.bSizer2.return_value()
        fmt = self.bSizer3.return_value()
        depth_scale = self.bSizer4.return_value()
        if age_file:
            depth_scale='age'
        elif depth_scale:
            depth_scale = 'sample_core_depth' #'mbsf'
        else:
            depth_scale = 'sample_composite_depth' #'mcd'
        dmin = self.bSizer5.return_value() or -1
        dmax = self.bSizer6.return_value() or -1

        # for use as module:
        self.okButton.Disable()
        self.wait = wx.BusyInfo("Please wait, generating plot...")
        args = [ani_file, meas_file, samp_file, age_file, fmt, float(dmin), float(dmax), depth_scale]
        PlotThread(self, ipmag.make_aniso_depthplot, args, self.make_plot_frame)
        #fig, figname = ipmag.make_aniso_depthplot(ani_file, meas_file, samp_file, age_file, fmt, float(dmin), float(dmax), depth_scale)
        #if fig:
        #    self.Destroy() 
        #    dpi = fig.get_dpi()
        #    pixel_width = dpi * fig.get_figwidth()
        #    pixel_height = dpi * fig.get_figheight()
        #    plot_frame = PlotFrame((pixel_width, pixel_height + 50), fig, figname)
        #else:
        #    pw.simple_warning("No data points met your criteria - try again\nError message: {}".format(figname))

        
        ## for use as command_line:
        #ani_file = "-f " + os.path.basename(ani_file)
        #meas_file = "-fb " + os.path.basename(meas_file)
        #if use_sampfile:
        #    samp_file = "-fsa " + os.path.basename(samp_file)
        #    age_file = ''
        #else:
        #    age_file = "-fa " + os.path.basename(age_file)
        #    samp_file = ''
        #if dmin and dmax:
        #    depth = "-d " + dmin + " " + dmax
        #else:
        #    depth = ''
        #depth_scale = "-ds " + depth_scale
        #fmt = "-fmt " + fmt
        #WD = "-WD " + self.WD

        #COMMAND = "ANI_depthplot.py {} {} {} {} {} {} {} {} -sav".format(WD, ani_file, meas_file, samp_file, age_file, depth, depth_scale, fmt)
        #print COMMAND
        ##pw.run_command_and_close_window(self, COMMAND, "er_samples.txt")
        #pw.run_command(self, COMMAND, "??")


        
    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton("ANI_depthplot.py -h")




class something(wx.Frame):

    title = ""
    
    def __init__(self, parent, WD):
        wx.Frame.__init__(self, parent, wx.ID_ANY, self.title)
        self.panel = wx.ScrolledWindow(self)
        self.WD = WD
        self.InitUI()

    def InitUI(self):
        pnl = self.panel
        TEXT = "some text"
        bSizer_info = wx.BoxSizer(wx.HORIZONTAL)
        bSizer_info.Add(wx.StaticText(pnl, label=TEXT), wx.ALIGN_LEFT)

        #---sizer 0 ----
        self.bSizer0 = pw.choose_file(pnl, 'add', method = self.on_add_file_button)

        #---sizer 1 ----
        self.bSizer1 = pw.specimen_n(pnl)

        #---sizer 2 ---
        self.bSizer2 = pw.select_ncn(pnl)

        #---sizer 3 ---
        self.bSizer3 = pw.labeled_text_field(pnl, label="Location name:")

        #---sizer 4 ---
        


        #---sizer 4 ----
        #try:
        #    open(self.WD + "/er_samples.txt", "rU")
        #except Exception as ex:
        #    er_samples_file_present = False
        #if er_samples_file_present:
        #    self.bSizer4 = pw.labeled_yes_or_no(pnl, TEXT, label1, label2)

        #---buttons ---
        hboxok = pw.btn_panel(self, pnl)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.LEFT, border=5)
        hbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT)
        vbox.Add(bSizer_info, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer0, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer1, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(self.bSizer2, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        vbox.Add(hbox, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #vbox.Add(self.bSizer3, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #try:
        #    vbox.Add(self.bSizer4, flag=wx.ALIGN_LEFT|wx.TOP, border=10)
        #except AttributeError:
        #    pass
        vbox.Add(hboxok, flag=wx.ALIGN_CENTER)        
        vbox.AddSpacer(20)

        hbox_all = wx.BoxSizer(wx.HORIZONTAL)
        hbox_all.AddSpacer(20)
        hbox_all.AddSpacer(vbox)

        self.panel.SetSizer(hbox_all)
        self.panel.SetScrollbars(20, 20, 50, 50)
        hbox_all.Fit(self)
        self.Show()
        self.Centre()

    def on_add_file_button(self,event):
        text = "choose file to convert to MagIC"
        pw.on_add_file_button(self.bSizer0, self.WD, event, text)

    def on_okButton(self, event):
        COMMAND = ""
        print COMMAND
        #pw.run_command_and_close_window(self, COMMAND, "er_samples.txt")

    def on_cancelButton(self,event):
        self.Destroy()
        self.Parent.Raise()

    def on_helpButton(self, event):
        pw.on_helpButton(".py -h")





        
# File

class ClearWD(wx.MessageDialog):

    def __init__(self, parent, WD):
        msg = "Are you sure you want to delete the contents of:\n{} ?\nThis action cannot be undone".format(WD)
        super(ClearWD, self).__init__(None, caption="Not so fast", message=msg, style=wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
        result = self.ShowModal()
        self.Destroy()
        if result == wx.ID_YES:
            #os.system('rm -r {}'.format(WD))
            os.chdir('..')
            import shutil
            shutil.rmtree(WD)
            os.mkdir(WD)
            os.chdir(WD)
            print "{} has been emptied".format(WD)
        else:
            print "{} has not been emptied".format(WD)


            

#consider using this instead (will preserve permissions of directory, but this may or may not be crucial)
#def emptydir(top):
#    if(top == '/' or top == "\\"): return
#    else:
#        for root, dirs, files in os.walk(top, topdown=False):
#            for name in files:
#                os.remove(os.path.join(root, name))
#            for name in dirs:
#                os.rmdir(os.path.join(root, name))


class PlotFrame(wx.Frame):
    def __init__(self, size, figure, figname):
        super(PlotFrame, self).__init__(None, -1, size=size)
        self.figure = figure
        self.figname = figname
        panel = wx.Panel(self, -1)
        canvas = FigureCanvas(panel, -1, self.figure)
        btn_panel = self.make_btn_panel()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, wx.LEFT | wx.TOP | wx.GROW) # having/removing wx.GROW doesn't matter
        sizer.Add(btn_panel, flag=wx.CENTRE|wx.ALL, border=5)
        panel.SetSizer(sizer)
        sizer.Fit(panel) # MIGHT HAVE TO TAKE THIS LINE OUT!!!
        self.Centre()
        self.Show()


    def make_btn_panel(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        btn_save = wx.Button(self, -1, "Save plot")
        self.Bind(wx.EVT_BUTTON, self.on_save, btn_save)
        btn_discard = wx.Button(self, -1, "Discard plot")
        self.Bind(wx.EVT_BUTTON, self.on_discard, btn_discard)
        hbox.AddMany([(btn_save, 1, wx.RIGHT, 5), (btn_discard)])
        return hbox

    def on_save(self, event):
        plt.savefig(self.figname)
        dlg = wx.MessageDialog(None, message="Plot saved as {}".format(self.figname), style=wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        self.Destroy()

    def on_discard(self, event):
        dlg = wx.MessageDialog(self, "Are you sure you want to delete this plot?", "Not so fast", style=wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
        response = dlg.ShowModal()
        if response == wx.ID_YES:
            dlg.Destroy()
            self.Destroy()
        

