# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
from mod_log import logger as logger
import modConfig as modConfig
import time

ClientSystem = clientApi.GetClientSystemCls()
comp = clientApi.GetEngineCompFactory()


class CodingTestClientSystem(ClientSystem):
    def __init__(self, namespace, systemName):
        super(CodingTestClientSystem, self).__init__(namespace, systemName)
        logger.info('[suc] ClientSystemInit')
        self.isExistVirtualWorld = False
        self.ListenEvents()
        self.virtualWorldComp = comp.CreateVirtualWorld(clientApi.GetLevelId())
        self.RepeatShoot = None
        self.SquidSwitch = None
        self.CanShoot = True
        self.objId = None
        self.corId = None
        self.shadow = None
        self.shoot_pit = -20
        self.shoot_power = 3.9
        self.shoot_gravity = 1
        self.player_moving = False

    def ListenEvents(self):
        """监听网易事件"""
        self.listen_custom_event()
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'UiInitFinished', self, self.OnUiInitFinished)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'OnKeyPressInGame', self, self.OnPress)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'OnKeyPressInGame', self, self.on_entity_inside)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'OnStandOnBlockClientEvent', self, self.OnStandBlock)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'WalkAnimBeginClientEvent', self, self.OnWalkBegin)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'WalkAnimEndClientEvent', self, self.OnWalkEnd)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'OnEntityInsideBlockClientEvent', self, self.on_entity_inside)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'OnClientPlayerStartMove', self, self.set_moving)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'OnClientPlayerStopMove', self, self.set_moving_false)

    def listen_custom_event(self):
        """监听自定义事件"""
        self.ListenForEvent(modConfig.ModName, modConfig.ServerSystemName,
                            'bullet_hit', self, self.OnHit)
        self.ListenForEvent(modConfig.ModName, modConfig.ServerSystemName,
                            'CreateVirtualWorld', self, self.create_virtual_world)

    def OnUiInitFinished(self, data):
        logger.info('[suc] Ui init finished')
        # self.NotifyToServer('playerId', playerId)
        self.ReturnToServer({'operation': 'OnUiFinished'})
        self.ReturnToServer({'operation': 'SquidSwitch',
                             'SquidSwitch': True})
        self.ModelInit()
        self.UiInit()
        # 设置相机锚点
        clientApi.GetEngineCompFactory().CreateCamera(clientApi.GetLevelId()).SetCameraAnchor((0, 0.46, 0))
        # 设置相机偏移
        clientApi.GetEngineCompFactory().CreateCamera(clientApi.GetLevelId()).SetCameraOffset((0, 0.46, 0))
        clientApi.GetEngineCompFactory().CreateCamera(clientApi.GetLevelId()).SetFov(63)

    def create_sfx(self, pos, sfx):
        """
        创建序列帧特效
        :param pos: 特效创建位置
        :param sfx: 特效名称
        :return:
        """
        frameEntityId = self.CreateEngineSfxFromEditor("effects/%s.json" % sfx)

        frameAniTransComp = clientApi.GetEngineCompFactory().CreateFrameAniTrans(frameEntityId)
        frameAniTransComp.SetPos(pos)
        frameAniTransComp.SetScale((1, 1, 1))

        frameAniControlComp = clientApi.GetEngineCompFactory().CreateFrameAniControl(frameEntityId)
        frameAniControlComp.SetUsePointFiltering(True)
        print frameAniControlComp.Play()
        # return frameAniControlComp.Play()
        # 停止序列帧
        # comp.CreateGame(clientApi.GetLevelId()).AddTimer(0.1, clientApi.GetEngineCompFactory().CreateFrameAniControl(frameEntityId).Stop())

    def removeSfx(self, frameEntityId):
        self.DestroyEntity(frameEntityId)

    def ModelInit(self):
        """骨骼模型初始化"""
        logger.info('[suc] Model init')
        # playerModel
        # Player模型comp
        playerId = clientApi.GetLocalPlayerId()
        PlayerModel = clientApi.GetEngineCompFactory().CreateModel(playerId)
        PlayerModel.SetModel('Player_steve')

        # 动画
        modelId = PlayerModel.GetModelId()
        PlayerModel.ModelPlayAni(modelId, "idle", True, False)
        # clientApi.GetEngineCompFactory().CreateModel(playerId).SetFreeModelScale(modelId, 0.483, 0.483, 0.483)

        # 把名称为gun的骨骼模型挂接到modelId为11的模型的rightHand骨骼上
        gunModelId = clientApi.GetEngineCompFactory().CreateModel(11).BindModelToModel("head", "splattershot")
        logger.info('[debug] 枪械模型绑定: %s' % gunModelId)

        # 模型ID
        logger.info('[debug] 玩家模型ID: %s' % modelId)

    def UiInit(self):
        """UI初始化"""
        logger.info('[warn] UI init')
        playerId = clientApi.GetLocalPlayerId()
        # 创建一个绑定在玩家头顶的UI
        print clientApi.RegisterUI(modConfig.ModName, modConfig.UIName, modConfig.UICls, 'ui0.main')
        print clientApi.CreateUI(
            modConfig.ModName,
            modConfig.UIName,
            {"isHud": 1
             # "bindEntityId": playerId,
             # "bindOffset": (0, 1, 0),
             # "autoScale": 1
             }
        )
        clientApi.RegisterUI(modConfig.ModName, modConfig.UIName1, modConfig.UICls, 'ui1.main')

    def ReturnToServer(self, args):
        """服务器回调封装"""
        response = args
        response['playerId'] = clientApi.GetLocalPlayerId()
        self.NotifyToServer('ActionEvent', args)

    def create_virtual_world(self, data):
        """负责监听文字输入，然后开关虚拟世界"""
        state = data['state']
        if state == "create":
            self.create_world()
        elif state == "close":
            result = self.virtualWorldComp.VirtualWorldDestroy()
            # 重置环境
            if result:
                self.isExistVirtualWorld = False
        elif state == 'GetPos':
            print self.virtualWorldComp.CameraGetPos()

    def create_world(self):
        """创建虚拟世界"""
        clientApi.CreateUI(
            modConfig.ModName,
            modConfig.UIName1,
            {"isHud": 1}
        )
        result = self.virtualWorldComp.VirtualWorldCreate()
        # 判断是否创建成功
        if result:
            self.isExistVirtualWorld = True
        else:
            return

        self.virtualWorldComp.VirtualWorldSetSkyTexture('textures/vsky', 1)
        self.virtualWorldComp.VirtualWorldSetCollidersVisible(True)

        # self.virtualWorldComp.CameraSetPos((0, 15, 5))
        # self.virtualWorldComp.CameraLookAt((0, 0, -13), (0, 1, 0))

        self.objId = self.virtualWorldComp.ModelCreateObject('datiangou', 'run')
        self.corId = self.virtualWorldComp.ModelCreateObject('coordinate', 'idle')
        self.shadow = self.virtualWorldComp.ModelCreateObject('datiangou_shadow', 'run')
        self.virtualWorldComp.ModelSetPos(self.corId, (0, 0, 0))
        self.virtualWorldComp.ModelSetPos(self.objId, (0, 0, 0))
        self.virtualWorldComp.ModelSetPos(self.shadow, (-0.094199, 0.181926, -0.249838))
        # self.virtualWorldComp.ModelSetRot(self.objId, (0, 180, 0))
        self.virtualWorldComp.ModelSetScale(self.objId, (1, 1, 1))
        self.virtualWorldComp.ModelSetScale(self.corId, (1, 1, 1))
        self.virtualWorldComp.ModelSetScale(self.shadow, (1, 1, 1))
        self.testing_logger('获取objId', self.objId)
        self.testing_logger('获取corId', self.corId)

    def testing_logger(self, event, info):
        logger.info('[debug] %s：%s' % (event, info))
        # print 'Testing logger'

    def OnPress(self, data):
        key = data['key']
        is_down = data['isDown']
        playerId = clientApi.GetLocalPlayerId()
        modelId = clientApi.GetEngineCompFactory().CreateModel(playerId).GetModelId()
        press_down = is_down == '1'
        press_up = is_down == '0'
        up_vector = (0, 1, 0)

        if is_down == '1':
            logger.info('[debug] 按下了 %s 键' % key)

        pos = {
            '0': (0.235731, 1.63182, 3.46268),
            '1': (-1.11729, 0.835222, 2.15922),
            '2': (0.007182, 1.87874, -3.37651)
        }
        target = {
            '0': (1.3137, 2.01009, -0.358237),
            '1': (1.02081, 1.64583, 0.017386),
            '2': (0.01043, 1.75862, 0.214952)
        }
        time_ease = clientApi.GetMinecraftEnum().TimeEaseType.in_out_quint

        # 虚拟相机
        if key == '49' and press_down:
            self.virtualWorldComp.CameraMoveTo((0.235731, 1.63182, 3.46268),
                                               (1.3137, 2.01009, -0.358237),
                                               up_vector, 1, 0.3, time_ease)
            self.virtualWorldComp.ModelPlayAnimation(self.objId, 'run', True, True, 3)
            self.virtualWorldComp.ModelPlayAnimation(self.shadow, 'run', True, True, 3)
        elif key == '50' and press_down:
            self.virtualWorldComp.CameraMoveTo((-1.11729, 0.835222, 2.15922),
                                               (1.02081, 1.64583, 0.017386),
                                               up_vector, 1, 0.3, time_ease)
            self.virtualWorldComp.ModelPlayAnimation(self.objId, 'attack', True, True, 2)
            self.virtualWorldComp.ModelPlayAnimation(self.shadow, 'attack', True, True, 3)

        elif key == '51' and press_down:
            self.virtualWorldComp.CameraMoveTo((3.31746, 1.31489, 3.83348),
                                               (1.44958, 2.10653, -0.99007),
                                               up_vector, 1, 0.5, time_ease)
            self.virtualWorldComp.ModelPlayAnimation(self.objId, 'fengxi', True, True, 1)
            self.virtualWorldComp.ModelPlayAnimation(self.shadow, 'fengxi', True, True, 1)

        # 设置射击强度 power
        if key == '104' and press_down:
            self.shoot_power += 0.1
            self.ReturnToServer({'operation': 'shoot_power',
                                 'power': self.shoot_power})
        elif key == '101' and press_down:
            self.shoot_power -= 0.1
            self.ReturnToServer({'operation': 'shoot_power',
                                 'power': self.shoot_power})

        # 设置射击重力 gravity
        if key == '105' and press_down:
            self.shoot_gravity += 0.1
            self.ReturnToServer({'operation': 'shoot_gravity',
                                 'gravity': self.shoot_gravity})
        elif key == '102' and press_down:
            self.shoot_gravity -= 0.1
            self.ReturnToServer({'operation': 'shoot_gravity',
                                 'gravity': self.shoot_gravity})

        # 跳跃按钮
        if key == '70' and press_down:
            clientApi.GetEngineCompFactory().CreateModel(playerId).PlayAnim('attack', False)
        elif data['key'] == '32' and is_down == '1':
            self.Anim1D()
        elif key == '84' and press_down:
            clientApi.GetEngineCompFactory().CreateModel(playerId).ModelPlayAni(modelId, "walk", True, False)

        # 射击开关
        if key == '70' and press_down:
            logger.info('[suc] 启动持续射击 1')
            self.Shoot()
            self.RepeatShoot = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).AddRepeatedTimer(0.1,
                                                                                                                    self.Shoot)
        elif key == '70' and is_down == '0':
            logger.info('[warn] 关闭持续射击 1')
            clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).CancelTimer(self.RepeatShoot)

        # todo 枪械模型挂接
        # if key == '100' and is_down == '1':
        #     logger.info('[debug] 挂接模型')
        #     comp.CreateModel(
        #         clientApi.GetEngineCompFactory().CreateModel(playerId).GetModelId()
        #     ).BindModelToModel(
        #         'rightitem', 'splattershot'
        #     )
        # elif key == '101' and is_down == '1':
        #     logger.info('[debug] 取消挂接')

        # todo 粒子挂接
        # if key == '103' and is_down == '1':
        #     logger.info('[suc] 挂接特效粒子')
        #     # 创建特效粒子
        #     particleEntityId = self.CreateEngineParticle(
        #         'effects/testing_particle.json',
        #         (0, 0, 0)
        #     )
        #     # 绑定特效粒子
        #     print comp.CreateParticleSkeletonBind(particleEntityId).Bind(
        #         clientApi.GetEngineCompFactory().CreateModel(playerId).GetModelId(),
        #         'waist',
        #         (0, 0, 0),
        #         (0, 0, 0)
        #     )
        #     # 播放特效粒子
        #     print comp.CreateParticleControl(particleEntityId).Play()
        # elif key == '104' and is_down == '1':
        #     logger.info('[error] 取消挂接粒子')

        # shift按下
        if key == '67' and is_down == '1':
            logger.info('[debug] 鱿鱼 down')
            self.ReturnToServer({'operation': 'isSquid'})
            self.SquidSwitch = True
        elif key == '67' and is_down == '0':
            logger.info('[debug] 鱿鱼 up')
            self.CanShoot = True
            self.ReturnToServer({'operation': 'notSquid'})
            self.SquidSwitch = False
            comp.CreateModel(playerId).ShowModel(
                clientApi.GetEngineCompFactory().CreateModel(playerId).GetModelId()
            )
            comp.CreateModel(playerId).SetEntityOpacity(1)

        angle = 1
        if key == '109' and press_down:
            self.shoot_pit -= angle
            self.ReturnToServer({'operation': 'shoot_yaw',
                                 'value': self.shoot_pit})
            # logger.info('[debug] 减少 %s 角度' % angle)
        elif key == '107' and press_down:
            self.shoot_pit += angle
            self.ReturnToServer({'operation': 'shoot_yaw',
                                 'value': self.shoot_pit})
            # logger.info('[debug] 增加 %s 角度' % angle)

        if key == '103' and press_down:
            self.camera_animation()

    def OnStandBlock(self, data):
        """当玩家站在特殊方块上"""
        playerId = clientApi.GetLocalPlayerId()
        blockName = data['blockName']
        # logger.info('[debug] [%s]站在方块[%s]上' % (entityId, blockName))
        if self.SquidSwitch and data['entityId'] == playerId:
            self.CanShoot = False

        # 隐藏鱿鱼模型
        if self.SquidSwitch and blockName == 'othniel:testing_block' and data['entityId'] == playerId:
            comp.CreateModel(playerId).HideModel(
                clientApi.GetEngineCompFactory().CreateModel(playerId).GetModelId()
            )
            # 隐藏模型的影子
            comp.CreateModel(playerId).SetEntityOpacity(0)
            # 启动粒子
            ParticleEntityId = self.CreateEngineParticle(
                'effects/testing_particle.json',
                (0, 0, 0)
            )
            comp.CreateParticleSkeletonBind(ParticleEntityId).Bind(
                clientApi.GetEngineCompFactory().CreateModel(playerId).GetModelId(),
                'root',
                (0, 1, 0),
                (0, 0, 0)
            )
            # 改变最大速度
            self.ReturnToServer({'operation': 'SquidSwitch',
                                 'SquidSwitch': True})
            # 设置墨水中的增速
            inkScale = 1.38
            data['motionX'] *= inkScale
            data['motionZ'] *= inkScale
            # logger.info('[debug] inkScale: %s' % inkScale)

        if blockName == 'othniel:iron_mesh' and self.SquidSwitch:
            # 铁丝网
            logger.info('[suc] 站在铁丝网上，客户端事件')
            # foot pos
            foot_pos = clientApi.GetEngineCompFactory().CreatePos(playerId).GetFootPos()
            self.ReturnToServer({'operation': 'iron_mesh',
                                 'foot_pos': foot_pos})

        # 非墨水方块则还原
        if blockName != ['othniel:testing_block', 'othniel:iron_mesh']:
            # 显示模型
            self.CanShoot = True
            comp.CreateModel(playerId).ShowModel(
                clientApi.GetEngineCompFactory().CreateModel(playerId).GetModelId()
            )
            comp.CreateModel(playerId).SetEntityOpacity(1)
            self.ReturnToServer({'operation': 'SquidSwitch',
                                 'SquidSwitch': False})

    def on_entity_inside(self, data):
        """监测到玩家碰撞箱在方块中则触发"""
        # entityId = data['entityId']
        # print data
        if self.player_moving and self.SquidSwitch:
            comp.CreateActorMotion(data['entityId']).SetMotion((0, 0.3, 0))

    def Shoot(self):
        """射击主逻辑"""
        # todo 如果连点发射键则会比原定的发射速度更快。需要设置时间锁
        # todo 前半段射击无散射，后半段才会有散射
        playerId = clientApi.GetLocalPlayerId()
        if self.CanShoot:
            # 播放开枪音效
            # logger.info('[debug] PlaySound %s')
            comp.CreateCustomAudio(playerId).PlayCustomMusic("splt:bullet_shoot", (0, 0, 0), 1, 1, False, playerId)
            # 传递到服务端
            # logger.info('[warn] 射击一发子弹')
            Pos = comp.CreatePos(playerId).GetPos()
            Dir = clientApi.GetDirFromRot(comp.CreateRot(playerId).GetRot())
            self.ReturnToServer({'operation': 'Shoot',
                                 'Pos': Pos,
                                 'Dir': Dir})

    def OnHit(self, data):
        # 检测生物受到伤害
        playerId = data['srcId']

        if data['targetId'] != '-1':
            logger.info('[suc] On hit entity %s' % data['targetId'])
            comp.CreateCustomAudio(playerId).PlayCustomMusic("splt:bullet_hit", (0, 0, 0), 1, 1, False, playerId)
            x = data['x']
            y = data['y']
            z = data['z']
            pos = (x, y, z)

            self.create_sfx(pos, 'hit_blue')
        # if data['targetId'] == '-1':
        #     logger.info('[error] No entity hit')
        # comp.CreateCustomAudio(playerId).PlayCustomMusic()

    def Anim1D(self):
        # logger.info('[debug] 启动Anim1D')
        playerId = clientApi.GetLocalPlayerId()
        compAnim = clientApi.GetEngineCompFactory().CreateModel(playerId)
        modelId = compAnim.GetModelId()

        compAnim.RegisterAnim1DControlParam(modelId, "idle", "jump", "alpha")
        compAnim.SetAnim1DControlParam(modelId, "alpha", 0.8)

        # 相继播放这两个动画，设置isBlend为True，开启动画混合。
        compAnim.ModelPlayAni(modelId, "idle", True, True)
        compAnim.ModelPlayAni(modelId, "jump", False, True)

    def OnWalkBegin(self, data):
        """识别玩家走路时"""
        playerId = clientApi.GetLocalPlayerId()
        PlayerModel = clientApi.GetEngineCompFactory().CreateModel(playerId)
        modelId = PlayerModel.GetModelId()
        PlayerModel.ModelPlayAni(modelId, "walk", True, False)

    def OnWalkEnd(self, data):
        playerId = clientApi.GetLocalPlayerId()
        PlayerModel = clientApi.GetEngineCompFactory().CreateModel(playerId)
        modelId = PlayerModel.GetModelId()
        PlayerModel.ModelPlayAni(modelId, "idle", True, False)

    def camera_animation(self, start_pos=0, end_pos=1, total_time=3, divided=10):
        """
        todo 相机动画函数
        :param start_pos: 起始位置
        :param end_pos: 结束位置
        :param total_time: 总时长
        :param divided: 细分次数
        :return:
        """
        # 内置参数
        current_time = 0
        step = (end_pos - start_pos) / divided
        per_time = total_time / divided

        while current_time < total_time:
            # esasing function: linar
            x = current_time

            current_time += 0.1
            print x
            time.sleep(per_time)

            if current_time == total_time:
                break

    def camera_run(self, x, y, z):
        logger.info('[suc] %s %s %s' % (x, y, z))

    def set_moving(self):
        # print 'is moving'
        self.player_moving = True

    def set_moving_false(self):
        # print 'stop moving'
        self.player_moving = False

    # 监听引擎ScriptTickClientEvent事件，引擎会执行该tick回调，1秒钟30帧
    def OnTickClient(self):
        """
        Driven by event, One tick way
        """
        pass

    # 被引擎直接执行的父类的重写函数，引擎会执行该Update回调，1秒钟30帧
    def Update(self):
        """
        Driven by system manager, Two tick way
        """
        pass

    def Destroy(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              'UiInitFinished', self, self.OnUiInitFinished)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              'OnKeyPressInGame', self, self.OnPress)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              'OnStandOnBlockClientEvent', self, self.OnStandBlock)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              'WalkAnimBeginClientEvent', self, self.OnWalkBegin)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              'WalkAnimEndClientEvent', self, self.OnWalkEnd)
        self.UnListenForEvent(modConfig.ModName, modConfig.ServerSystemName,
                              'bullet_hit', self, self.OnHit)
        self.UnListenForEvent(modConfig.ModName, modConfig.ServerSystemName,
                              'CreateVirtualWorld', self, self.create_virtual_world)
