class SkillUpgrade:
    def __init__(self, id, name, description, cost, dependencies=None):
        self.id = id
        self.name = name
        self.description = description
        self.cost = cost
        self.dependencies = dependencies or []
        self.is_unlocked = False

class SkillDefinition:
    def __init__(self, id, name, description, cost):
        self.id = id
        self.name = name
        self.description = description
        self.cost = cost
        self.is_learned = False
        self.level = 0
        self.upgrades = {}

    def add_upgrade(self, upgrade):
        self.upgrades[upgrade.id] = upgrade

class SkillTree:
    def __init__(self):
        self.skills = {}
        self._initialize_skills()

    def _initialize_skills(self):
        # --- Dash Skill ---
        dash = SkillDefinition("dash", "冲刺", "快速向指定方向位移。", 100)
        dash.add_upgrade(SkillUpgrade("dash_blood", "血魔宗", "闪现对路径上的敌人造成伤害。", 50))
        dash.add_upgrade(SkillUpgrade("dash_hegemon", "霸体宗", "闪现后获得0.5秒无敌。", 50))
        self.skills[dash.id] = dash
        
        # --- Add other skills here in the future ---

    def can_unlock(self, skill_id, upgrade_id, player_points):
        skill_def = self.skills.get(skill_id)
        upgrade = skill_def.upgrades.get(upgrade_id)
        if not skill_def or not upgrade or not skill_def.is_learned or upgrade.is_unlocked:
            return False
        if player_points < upgrade.cost:
            return False
        if skill_def.level >= 2: # Max level reached
            return False
        
        # Check dependencies
        for dep_id in upgrade.dependencies:
            if not skill_def.upgrades[dep_id].is_unlocked:
                return False
        return True

    def unlock_upgrade(self, skill_id, upgrade_id):
        skill_def = self.skills[skill_id]
        upgrade = skill_def.upgrades[upgrade_id]
        upgrade.is_unlocked = True
        skill_def.level += 1
