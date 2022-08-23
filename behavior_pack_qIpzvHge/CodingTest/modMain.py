# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
import modConfig as modConfig
from mod_log import logger as logger

@Mod.Binding(name="CodingTest", version="0.0.1")
class CodingTest(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def CodingTestServerInit(self):
        logger.info('[warn] ServerRegister')
        serverApi.RegisterSystem(modConfig.ModName, modConfig.ServerSystemName, modConfig.ServerClsPath)

    @Mod.InitClient()
    def CodingTestClientInit(self):
        logger.info('[warn] ClientRegister')
        clientApi.RegisterSystem(modConfig.ModName, modConfig.ClientSystemName, modConfig.ClientClsPath)
