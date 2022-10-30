from .img import ImageAgent 

# This class only extracts Texture2D from env_
class EnvironmentAgent(ImageAgent):
    def pre_check(self) -> bool:
        return self.slug.startswith("env_")
