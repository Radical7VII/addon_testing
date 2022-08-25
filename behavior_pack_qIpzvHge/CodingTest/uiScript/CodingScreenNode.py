# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from mod_log import logger as logger

ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class CodingScreenNode(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        # 主面板路径
        self.panel_path = '/panel'
        self.client_system = clientApi.GetSystem('CodingTest', 'CodingClient')

    def Create(self):
        """
        @description UI创建成功时调用
        """
        # 获取实例
        self.panel_item = self.GetBaseUIControl(self.panel_path)
        # 按钮注册
        self.start_button = self.panel_item.GetChildByPath('/start').asButton()
        self.up_button = self.panel_item.GetChildByPath('/up').asButton()
        self.down_button = self.panel_item.GetChildByPath('/down').asButton()
        # 设置按钮回调
        self.start_button.AddTouchEventParams({'isSwallow': True})
        self.start_button.SetButtonTouchUpCallback(self.button_touchback)
        self.up_button.AddTouchEventParams({'isSwallow': True})
        self.up_button.SetButtonTouchUpCallback(self.up_button_callback)
        self.down_button.AddTouchEventParams({'isSwallow': True})
        self.down_button.SetButtonTouchUpCallback(self.down_button_callback)

    def button_touchback(self, data):
        # logger.info('[suc] 按钮成功回调')

        player_foot_pos = clientApi.GetEngineCompFactory().CreatePos(clientApi.GetLocalPlayerId()).GetFootPos()
        self.client_system.create_sfx((player_foot_pos[0] + -1, player_foot_pos[1] + 1, player_foot_pos[2] + 1.2),
                                      (0, -45, 0),
                                      (0.5, 0.5, 0.5),
                                      'effects/holo_green.json'
                                      )
        self.client_system.create_sfx((player_foot_pos[0] + -1.2, player_foot_pos[1] + 1, player_foot_pos[2] + 1.4),
                                      (0, -45, 0),
                                      (0.5, 0.5, 0.5),
                                      'effects/holo_frame.json'
                                      )
        comp = clientApi.GetEngineCompFactory().CreateCamera(clientApi.GetLevelId())
        comp.DepartCamera()
        comp.LockCamera((player_foot_pos[0], player_foot_pos[1] + 0.5, player_foot_pos[2] + 2.3),
                        (-16.89, 169.70))

    def up_button_callback(self, data):
        logger.info('[suc] press up')

    def down_button_callback(self, data):
        logger.info('[suc] press down')


def Destroy(self):
    """
    @description UI销毁时调用
    """
    pass


def OnActive(self):
    """
    @description UI重新回到栈顶时调用
    """
    pass


def OnDeactive(self):
    """
    @description 栈顶UI有其他UI入栈时调用
    """
    pass
