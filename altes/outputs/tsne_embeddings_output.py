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


class TSNEEmbeddingsOutput(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return None
        rep_list = []
        if data.get('mass_center', None) is not None:
            rep_list.append(data['mass_center']['rep'])
        rep_list.append(data['result'][0]['data']['rep'])
        for res_dict in data['result']:
            rep_list.append(res_dict['database']['rep'])
        # tsne = TSNE(n_components=2, init='random', random_state=0)
        # pca_list = PCA(n_components=50).fit_transform(rep_list, rep_list)
        # tsne_list = tsne.fit_transform(pca_list)
        # mds = MDS(n_components=2, n_init=1, max_iter=100)
        # tsne_list = mds.fit_transform(rep_list)
        srp = SparseRandomProjection(n_components=2, random_state=42)
        srp.fit(random_matrix)
        tsne_list = srp.transform(rep_list)
        print tsne_list
        colors = cm.Set1(np.linspace(0, 1, 3))
        print colors
        start = 1
        if data.get('mass_center', None) is not None:
            plt.scatter(tsne_list[0][0], tsne_list[0][1], c=colors[0], label="mass center")
            start += 1
        plt.scatter(tsne_list[start - 1][0], tsne_list[start - 1][1], c=colors[1], label="test")
        # for inx in range(start, len(tsne_list), 1):
        #     plt.scatter(tsne_list[inx:][0], tsne_list[inx:][1], c=colors[2], label="train")
        plt.plot([f[0] for f in tsne_list[start:]], [f[1] for f in tsne_list[start:]], 'or', label='train')
        test_emb = [tsne_list[start - 1][0], tsne_list[start - 1][1]]
        x = 0
        y = 0
        dist = 0
        for f in tsne_list[start:]:
            x += f[0]
            y += f[1]
            dist += distance.euclidean(test_emb, [f[0], f[1]])
        x /= 1.0 * len(tsne_list[start:])
        y /= 1.0 * len(tsne_list[start:])
        dist /= 1.0 * len(tsne_list[start:])
        print [x, y], dist
        plt.scatter(x, y, c=colors[2], label="em mass center")
        plt.legend()
        plt.show()
        return data
