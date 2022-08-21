# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi

from mod_log import logger as logger
import modConfig as modConfig
import random as random

comp = serverApi.GetEngineCompFactory()
ServerSystem = serverApi.GetServerSystemCls()


class CodingTestServerSystem(ServerSystem):
    def __init__(self, namespace, systemName):
        super(CodingTestServerSystem, self).__init__(namespace, systemName)
        logger.info('[warn] ServerSystemInit')
        self.ListenEvents()
        self.SquidSwitch = False
        self.random_range = True
        self.ShootRange = None
        self.shoot_gravity = 1
        self.shoot_pit = -20
        self.shoot_power = 3.8

    def ListenEvents(self):
        self.ListenForEvent(modConfig.ModName, modConfig.ClientSystemName,
                            'ActionEvent', self, self.OnClientAction)
        self.ListenForEvent(modConfig.ModName, modConfig.ClientSystemName,
                            'playerId', self, self.GetPlayerId)

        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            'OnStandOnBlockServerEvent', self, self.OnStandBlock)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            'JumpAnimBeginServerEvent', self, self.OnJump)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            "ProjectileDoHitEffectEvent", self, self.on_projectile_do_hit)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            'ServerChatEvent', self, self.ServerChatEvent)

    def OnClientAction(self, data):
        """检测到NotifyToClient时触发"""
        playerId = data['playerId']
        operation = data['operation']
        if operation != 'SquidSwitch':
            logger.info('[suc] 监听到客户端事件 %s ' % data)

        if operation == 'isSquid':
            self.isSquid(playerId)
        if operation == 'notSquid':
            self.NotSquid(playerId)
        if operation == 'OnUiFinished':
            self.OnUiFinished(playerId)

        if operation == 'SquidSwitch' and data['SquidSwitch'] is True:
            # 鱿鱼
            AttrSpeed = 3
            # logger.info('[suc] 设置最大速度为 %s' % AttrSpeed)
            serverApi.GetEngineCompFactory().CreateAttr(playerId).SetAttrMaxValue(
                serverApi.GetMinecraftEnum().AttrType.SPEED, AttrSpeed)
        if operation == 'SquidSwitch' and data['SquidSwitch'] is False:
            # 人类
            self.SetDefaultSpeed(playerId)
        if operation == 'Shoot':
            self.Shoot(data)
        if operation == 'shoot_yaw':
            self.shoot_pit = data['value']
            logger.info('[debug] 当前角度为 %s' % self.shoot_pit)
        if operation == 'shoot_power':
            self.shoot_power = data['power']
            logger.info('[suc] 设置power强度为 %s' % data['power'])
        if operation == 'shoot_gravity':
            self.shoot_gravity = data['gravity']
            logger.info('[suc] 设置gravity重量为 %s' % data['gravity'])
        # 踩在铁丝网上
        if operation == 'iron_mesh':
            self.on_iron_mesh(data)

    def SetDefaultSpeed(self, playerId):
        """设置玩家默认速度"""
        AttrSpeed = 0.12
        # logger.info('[suc] 设置最大速度为 %s' % AttrSpeed)
        comp.CreateAttr(playerId).SetAttrMaxValue(
            serverApi.GetMinecraftEnum().AttrType.SPEED, AttrSpeed)
        comp.CreateAttr(playerId).SetAttrValue(
            serverApi.GetMinecraftEnum().AttrType.SPEED, AttrSpeed)

    def OnUiFinished(self, data):
        logger.info('[warn] OnUiFinished')
        self.SetDefaultSpeed(data)

        # 临时注册方块事件
        serverApi.GetEngineCompFactory().CreateBlockInfo(serverApi.GetLevelId()).RegisterOnStandOn(
            "minecraft:wool", True)
        # serverApi.GetEngineCompFactory().CreateBlockInfo(serverApi.GetLevelId()).RegisterOnStandOn(
        #     "othniel:iron_mesh", True)

    def ServerChatEvent(self, data):
        temp_data = self.CreateEventData()
        message = data['message']
        if data['message'] == 'VW':
            temp_data['state'] = 'create'
            self.BroadcastToAllClient('CreateVirtualWorld', temp_data)
        elif data['message'] == 'CVW':
            temp_data['state'] = 'close'
            self.BroadcastToAllClient('CreateVirtualWorld', temp_data)
        elif message == 'get pos':
            temp_data = 'GetPos'
        if message == 'close':
            self.random_range = False
            print self.random_range
        if message == 'open':
            self.random_range = True
            print self.random_range

    def on_projectile_do_hit(self, data):
        """获取子弹落点坐标"""
        # logger.info('[debug] Projectile Do Hit %s' % data)
        block_posX = data['blockPosX']
        block_posY = data['blockPosY']
        block_posZ = data['blockPosZ']
        # todo:设置子弹溅射范围变大 将setblock替换为API接口
        # comp.CreateCommand(serverApi.GetLevelId()).SetCommand(
        #     '/setblock %s %s %s othniel:testing_block' % (block_posX, block_posY, block_posZ))
        blockDict = {
            'name': 'othniel:testing_block',
            'aux': 0
        }
        serverApi.GetEngineCompFactory().CreateBlockInfo(serverApi.GetLevelId()).SetBlockNew(
            (block_posX, block_posY, block_posZ), blockDict, 0, 0)

        bulletId = data['id']
        self.DestroyEntity(bulletId)
        # 传递告诉客户端，播放击中音效
        self.NotifyToClient(data['srcId'], 'bullet_hit', data)

    def isSquid(self, playerId):
        """
        鱿鱼状态下 设置模型为鱿鱼、碰撞盒为鱿鱼
        :param playerId: 玩家id
        :return:
        """
        # logger.info('[debug] ServerGet Squid Down')
        comp.CreateModel(playerId).SetModel('inkSquid3')
        comp.CreateCollisionBox(playerId).SetSize((0.8, 0.8))
        self.SquidSwitch = True

    def NotSquid(self, playerId):
        """
        人类状态下 设置模型为人类、碰撞盒为人类大小
        :param playerId: 玩家id
        :return:
        """
        # logger.info('[debug] ServerGet Squid up')
        comp.CreateModel(playerId).SetModel('Player_steve')
        comp.CreateCollisionBox(playerId).SetSize((0.88, 1.32))
        self.SquidSwitch = False

    def OnStandBlock(self, data):
        """检测站在方块上"""
        entityId = data['entityId']
        blockName = data['blockName']

    def on_iron_mesh(self, data):
        """如果站在铁丝网上则往下瞬移"""
        playerId = data['playerId']
        foot_pos = data['foot_pos']
        offset = 0.5

        x = foot_pos[0]
        y = foot_pos[1] - offset
        z = foot_pos[2]

        serverApi.GetEngineCompFactory().CreatePos(playerId).SetFootPos((x, y, z))
        logger.info('[debug] 站在铁丝网上 服务端data:%s, 偏移量:%s' % (data, offset))

    def GetPlayerId(self, data):
        logger.info('[warn] 获取玩家ID:%s' % data)
        self.ModelInit(data)

    def Shoot(self, data):
        # logger.info('[debug] %s' % data)
        playerId = data['playerId']

        PosList = list(data['Pos'])

        # 创建随机数。Pit对应垂直，Yaw对应左右。
        random_pit = random.uniform(-5, 5)
        random_yaw = random.uniform(-10, 10)
        # 获取玩家Rot
        RotList = serverApi.GetEngineCompFactory().CreateRot(playerId).GetRot()
        RotP = RotList[0]
        RotY = RotList[1]

        # 将玩家Rot与随机值相加。相加后再转换成Dir
        combine_pit = RotP + self.shoot_pit

        DirList = serverApi.GetDirFromRot(RotList)

        # 提取玩家坐标tuple
        PosX = PosList[0] + DirList[0]
        PosY = PosList[1] + DirList[1] - 0.3
        PosZ = PosList[2] + DirList[2]

        if not self.random_range:
            # 如果关闭随机散射，改为极限俯仰角
            self.ShootRange = serverApi.GetDirFromRot((
                RotP + self.shoot_pit,
                RotY))
        if self.random_range:
            # 打开随机散射
            self.ShootRange = serverApi.GetDirFromRot((
                RotP + random_pit + self.shoot_pit + -5,
                RotY + random_yaw))

        # 射击参数
        param = {
            'position': (PosX, PosY, PosZ),
            'direction': self.ShootRange,
            'power': self.shoot_power,
            'gravity': self.shoot_gravity,
            'damage': 36
        }
        comp.CreateProjectile(serverApi.GetLevelId()).CreateProjectileEntity(
            playerId, "minecraft:arrow", param)
        logger.info('[debug] 强度:%s，重力：%s，伤害：%s' % (param['power'], param['gravity'], param['damage']))

    def OnJump(self, data):
        # print data
        pass

    def ModelInit(self, data):
        # serverApi.GetEngineCompFactory().CreateModel(data).SetModel('datiangou')
        pass

    # ScriptTickServerEvent的回调函数，会在引擎tick的时候调用，1秒30帧（被调用30次）
    def OnTickServer(self):
        """
        Driven by event, One tick way
        """
        pass

    # 这个Update函数是基类的方法，同样会在引擎tick的时候被调用，1秒30帧（被调用30次）
    def Update(self):
        """
        Driven by system manager, Two tick way
        """
        pass

    def Destroy(self):
        pass
