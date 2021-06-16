import numpy as np
from pathlib import Path
from FRCommon.fr_config import CoreConfig


class FRFeatureLog:
    def __init__(self,):
        self.groupFeatures = {CoreConfig.groups: np.array([])}
        self.featureLoader()

    def featureLoader(self,):
        for npyfile in list(Path(CoreConfig.FR_FEATURE_DIR).glob("**/*.npy")):
            self.groupFeatures[npyfile.stem] = np.load(npyfile.as_posix())
        return True

    def featureSaver(self, grp_name):
        if grp_name == CoreConfig.groups:
            np.save((Path(CoreConfig.FR_FEATURE_DIR) / grp_name).as_posix(), self.groupFeatures[grp_name])
        else:
            grp_embeds, grp_ids = (
                grp_name + CoreConfig.grp_embeds,
                grp_name + CoreConfig.grp_ids,
            )
            np.save((Path(CoreConfig.FR_FEATURE_DIR) / grp_embeds).as_posix(), self.groupFeatures[grp_embeds])
            np.save((Path(CoreConfig.FR_FEATURE_DIR) / grp_ids).as_posix(), self.groupFeatures[grp_ids])
        return True

    def featureBackup(self):
        [
            self.featureSaver(grp_name=grp_name) for grp_name in self.groupFeatures.keys()
        ]
        return True

    def getEIDEmbed(self, grp_name, eid):
        grp_embeds, grp_ids = (
            grp_name + CoreConfig.grp_embeds,
            grp_name + CoreConfig.grp_ids,
        )
        temp = self.groupFeatures[grp_embeds]\
            [np.where(self.groupFeatures[grp_ids] == eid)[0][0]]
        return temp.reshape(1,-1)

    def embedGrouping(self, grp_name, face_embedding, face_id):
        """
        group_list (CoreConfig.groups), embed list (CoreConfig.grp_embeds), ids list (CoreConfig.grp_ids)
        all are in one single Hash(Dict) level to optimize time during listing all groups and 
        saving/loading as npy files and while indexing for search
        """
        grp_embeds, grp_ids = (
            grp_name + CoreConfig.grp_embeds,
            grp_name + CoreConfig.grp_ids,
        )
        if grp_embeds in self.groupFeatures:
            self.groupFeatures[grp_embeds] = np.vstack(
                (self.groupFeatures[grp_embeds], face_embedding)
            )
            self.groupFeatures[grp_ids] = np.vstack(
                (self.groupFeatures[grp_ids], np.array(face_id))
            )
        else:
            print(type(self.groupFeatures[CoreConfig.groups]),self.groupFeatures[CoreConfig.groups])
            self.groupFeatures[grp_embeds] = face_embedding
            self.groupFeatures[grp_ids] = np.array(face_id)
            self.groupFeatures[CoreConfig.groups] = np.append(self.groupFeatures[CoreConfig.groups],grp_name)
            self.featureSaver(CoreConfig.groups)
        return True
