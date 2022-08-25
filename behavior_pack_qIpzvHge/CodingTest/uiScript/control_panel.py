# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class control_panel(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.aim_path = '/aim'
		self.control_path = '/control'
		self.client_system = clientApi.GetSystem('CodingTest', 'CodingClient')
		self.playerId = clientApi.GetLocalPlayerId()

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		self.control_item = self.GetBaseUIControl(self.control_path)
		# 按钮注册
		self.shoot_button = self.control_item.GetChildByPath('/shoot').asButton()
		self.squid_button = self.control_item.GetChildByPath('/squid').asButton()
		# 按钮回调
		self.shoot_button.AddTouchEventParams({'isSwallow': False})
		self.shoot_button.SetButtonTouchUpCallback(self.shoot_button_callback)
		self.squid_button.AddTouchEventParams({'isSwallow': False})
		self.squid_button.SetButtonTouchUpCallback(self.squid_button_callback)

	def shoot_button_callback(self, data):
		"""射击按钮按下"""
		print 'shoot button callback'
		self.client_system.Shoot()

	def squid_button_callback(self, data):
		print 'squid button callback'

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
