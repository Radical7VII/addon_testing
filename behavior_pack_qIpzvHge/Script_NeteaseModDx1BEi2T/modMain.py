# -*- coding: utf-8 -*-

from common.mod import Mod


@Mod.Binding(name="Script_NeteaseModDx1BEi2T", version="0.0.1")
class Script_NeteaseModDx1BEi2T(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def Script_NeteaseModDx1BEi2TServerInit(self):
        pass

    @Mod.DestroyServer()
    def Script_NeteaseModDx1BEi2TServerDestroy(self):
        pass

    @Mod.InitClient()
    def Script_NeteaseModDx1BEi2TClientInit(self):
        pass

    @Mod.DestroyClient()
    def Script_NeteaseModDx1BEi2TClientDestroy(self):
        pass
