class SkillUpgrade:
    def __init__(self, id, name, description, cost, dependencies=None):
        self.id = id
        self.name = name
        self.description = description
        self.cost = cost
        self.dependencies = dependencies or []
        self.is_unlocked = False

class Skill:
    def __init__(self, id, name, description, cost):
        self.id = id
        self.name = name
        self.description = description
        self.cost = cost
        self.is_learned = False
        self.upgrades = {}

    def add_upgrade(self, upgrade):
        self.upgrades[upgrade.id] = upgrade

class SkillTree:
    def __init__(self):
        self.skills = {}
        self._initialize_skills()

    def _initialize_skills(self):
        # --- Dash Skill ---
        dash = Skill("dash", "冲刺", "快速向指定方向位移。", 100)
        dash.add_upgrade(SkillUpgrade("dash_blood", "血魔宗", "闪现对路径上的敌人造成伤害。", 50))
        dash.add_upgrade(SkillUpgrade("dash_hegemon", "霸体宗", "闪现后获得0.5秒无敌。", 50))
        self.skills[dash.id] = dash
        
        # --- Add other skills here in the future ---

    def can_unlock(self, skill_id, upgrade_id, player_points):
        skill = self.skills.get(skill_id)
        upgrade = skill.upgrades.get(upgrade_id)
        if not skill or not upgrade or not skill.is_learned or upgrade.is_unlocked:
            return False
        if player_points < upgrade.cost:
            return False
        
        # Check dependencies
        for dep_id in upgrade.dependencies:
            if not skill.upgrades[dep_id].is_unlocked:
                return False
        return True

    def unlock_upgrade(self, skill_id, upgrade_id):
        upgrade = self.skills[skill_id].upgrades[upgrade_id]
        upgrade.is_unlocked = True
