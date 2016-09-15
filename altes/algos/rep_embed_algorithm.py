from server.biomio.algorithms.flows.base import IAlgorithm
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, MDS
from sklearn.random_projection import SparseRandomProjection
import matplotlib.pyplot as plt
import scipy.spatial.distance as distance
import matplotlib.cm as cm
import numpy as np

plt.style.use('bmh')
random_matrix = np.random.random((1, 128))


class RepEmbeddingsAlgorithm(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return None
        img_obj = data['img']
        # tsne = TSNE(n_components=2, init='random', random_state=0)
        # pca_list = PCA(n_components=50).fit_transform(rep_list, rep_list)
        # tsne_list = tsne.fit_transform(pca_list)
        # mds = MDS(n_components=2, n_init=1, max_iter=100)
        # tsne_list = mds.fit_transform(rep_list)
        srp = SparseRandomProjection(n_components=2, random_state=42)
        srp.fit(random_matrix)
        embeddings = srp.transform([img_obj.attribute('rep')])
        img_obj.attribute('embeddings', embeddings[0])
        return {'img': img_obj}
