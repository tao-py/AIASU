from Ui import (
    UIConfig, UIManager, ThemeEngine, AnimationEngine,
    Position, CandidateItem
)

# 自定义配置
config = UIConfig(
    theme="dark",
    opacity=0.95,
    animation_duration=200,
    max_candidates=8,
    follow_cursor=True,
    auto_hide_delay=3000
)

# 创建管理器
ui_manager = UIManager(config)
theme_engine = ThemeEngine("themes")
animation_engine = AnimationEngine()

# 设置依赖关系
ui_manager.set_theme_manager(theme_engine)
ui_manager.set_animation_controller(animation_engine)

# 创建和使用组件
overlay = ui_manager.show_component()  # 假设UIManager有创建overlay的方法
overlay.set_content("欢迎使用AIASU！")
overlay.show(Position(300, 300))