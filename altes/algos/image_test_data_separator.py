from server.biomio.algorithms.flows.base import IAlgorithm


RAWSTRUCT_SOURCE = "RawImagesStruct"
IMAGEDIR_SOURCE = "ImageDirectory"


class ImageTestDataSeparator(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        """
        Input:
        {
            'type': RawImagesStruct or ImageDirectory
            'train': altes.structs.RawImagesStruct
                     or altes.structs.ImageDirectory,
            'test': altes.structs.ImageContainer
        }
        :param data:
        :return:
        [
            {'type': ImageDirectory, 'train': altes.structs.ImageDirectory}
        or (and)
            {'img': altes.structs.ImageContainer}
        ]
        """
        if data is None:
            return data
        data_list = []
        if data.get('type', None) == RAWSTRUCT_SOURCE:
            struct = data['train']
            for struct_dirs in struct.directories():
                data_list.append({'type': IMAGEDIR_SOURCE, 'train': struct_dirs})
        elif data.get('type', None) == IMAGEDIR_SOURCE:
            dir_obj = data['train']
            for img_obj in dir_obj.images():
                data_list.append({'img': img_obj})
        if data.get('test', None) is not None:
            data_list.append({'img': data.get('test')})
        if data.get('img', None) is not None:
            data_list.append({'img': data.get('img')})
        return data_list
