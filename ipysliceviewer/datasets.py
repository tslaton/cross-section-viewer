# Standard lib
import os
import imghdr
# Third Party
import numpy as np
# Local
from .utils import PIL_to_numpy, bytes_to_PIL, normalize

class Dataset():
    """
    An abstract class representing a Dataset similar to the PyTorch api.

    Inheritors should implement __getitem__ and __len__.

    Ref: https://pytorch.org/docs/stable/_modules/torch/utils/data/dataset.html#Dataset
    """
    def __getitem__(self, index):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

class FolderDataset(Dataset):
    def __init__(self, directory):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise IOError(f"Not a valid directory: {directory}")

        self.directory = directory

        images = []
        for fname in os.listdir(directory):
            fpath = os.path.join(directory, fname)
            if os.path.isdir(fpath):
                continue
            if imghdr.what(fpath) is not None:
                images.append(fname)
        self.image_names = sorted(images)

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, idx):
        filepath = os.path.join(self.directory, self.image_names[idx])
        with open(filepath, 'rb') as f:
            image = f.read()
        return PIL_to_numpy(bytes_to_PIL(image))

    def filepath(self, idx):
        return os.path.join(self.directory, self.image_names[idx])

    def file_format(self, idx):
        return self.image_names[idx][:-4]

class VolumeDataset(Dataset):
    def __init__(self, volume):
        if not isinstance(volume, np.ndarray):
            raise TypeError("Not a numpy array: {}".format(volume))

        self.max = np.max(volume)
        self.min = np.min(volume)
        self.volume = normalize(volume)
        self.planes = ['yz', 'xz', 'xy']
        self.free_axis = 0

    @property
    def plane(self):
        return self.planes[self.free_axis]

    @plane.setter
    def plane(self, name):
        self.free_axis = self.planes.index(name)

    def __len__(self):
        return self.volume.shape[self.free_axis]

    def __getitem__(self, idx):
        cases = {
            0: lambda: self.volume[idx, :, :],
            1: lambda: self.volume[:, idx, :],
            2: lambda: self.volume[:, :, idx],
        }
        return cases[self.free_axis]()
