from corankco.dataset import DatasetSelector
from corankco.algorithms.algorithmChoice import get_algorithm, Algorithm
from corankco.algorithms.median_ranking import MedianRanking
from corankco.scoringscheme import ScoringScheme
from corankco.experiments.experiment import ExperimentFromDataset
from typing import List, Tuple
import numpy as np


class BenchTime(ExperimentFromDataset):

    def __init__(self,
                 dataset_folder: str,
                 algs: List[MedianRanking],
                 scoring_scheme: ScoringScheme,
                 dataset_selector_exp: DatasetSelector = None,
                 steps: int = 5,
                 max_time: float = float('inf'),
                 repeat_time_computation_until: float = 1.):

        super().__init__(dataset_folder, dataset_selector_exp)
        self.__algs = algs
        self.__scoring_scheme = scoring_scheme
        self.__steps = steps
        self.__max_time = max_time
        self.__repeat_time_computation_until = repeat_time_computation_until

    def _run_raw_data(self) -> str:
        res = ""
        ligne: str = "dataset;nb_elements"
        for alg in self.__algs:
            ligne += ";" + alg.get_full_name()
        ligne += "\n"
        self._write_line_in_file("/home/pierre/Bureau/res_bench.txt", ligne)
        res += ligne
        must_run = [True] * len(self.__algs)
        for dataset in sorted(self.datasets, key=lambda dataset_obj: dataset_obj.nb_elements):
            ligne: str = ""
            ligne += dataset.name + ";" + str(dataset.nb_elements)
            id_alg = 0
            for alg in self.__algs:
                if must_run[id_alg]:
                    time_computation = alg.bench_time_consensus(dataset,
                                                                self.__scoring_scheme,
                                                                True,
                                                                self.__repeat_time_computation_until)
                    ligne += ";" + str(time_computation)
                    if time_computation > self.__max_time:
                        must_run[id_alg] = False
                    id_alg += 1
                else:
                    ligne += ";" + str(float("inf"))
            ligne += "\n"
            self._write_line_in_file("/home/pierre/Bureau/res_bench.txt", ligne)
            res += ligne
        return res

    def _run_final_data(self, raw_data: str) -> str:
        res = "size_datasets"
        for alg in self.__algs:
            res += ";"+alg.get_full_name() + "_mean_time"
        res += "\n"
        h_res = {}
        mapping_nb_elements_group = {}
        cpt = 0
        key_mapping = 0
        h_res[0] = {}
        for alg in self.__algs:
            h_res[0][alg] = []
        tuples_groups = []
        for i in range(self._dataset_selector.nb_elem_min, self._dataset_selector.nb_elem_max+1):
            cpt += 1
            mapping_nb_elements_group[i] = key_mapping

            if cpt == self.__steps:
                key_mapping += 1
                cpt = 0
                h_res[key_mapping] = {}
                for alg in self.__algs:
                    h_res[key_mapping][alg] = []
        for i in range(self._dataset_selector.nb_elem_min, self._dataset_selector.nb_elem_max+1, self.__steps):
            tuples_groups.append((i, i+self.__steps-1))
        for line in raw_data.split("\n")[1:]:
            if len(line) > 1:
                cols = line.split(";")
                nb_elements = int(cols[1])
                col_first_alg = len(cols) - len(self.__algs)
                for j in range(col_first_alg, len(cols)):
                    h_res[mapping_nb_elements_group[nb_elements]][self.__algs[j-col_first_alg]].append(float(cols[j]))
        for i in range(len(tuples_groups)):
            tuple_i = tuples_groups[i]
            res += str(tuple_i)
            for alg in self.__algs:
                res += ";" + str(np.mean(np.asarray(h_res[i][alg])))
            res += "\n"
        return res

#######################################################################################################################


class BenchScalabilityScoringScheme(ExperimentFromDataset):

    def __init__(self,
                 dataset_folder: str,
                 alg: MedianRanking,
                 scoring_schemes: List[ScoringScheme],
                 dataset_selector_exp: DatasetSelector = None,
                 steps: int = 5,
                 max_time: float = float('inf'),
                 repeat_time_computation_until: float = 1.):

        super().__init__(dataset_folder, dataset_selector_exp)
        self.__alg = alg
        self.__scoring_schemes = scoring_schemes
        self.__steps = steps
        self.__max_time = max_time
        self.__repeat_time_computation_until = repeat_time_computation_until

    def _run_raw_data(self) -> str:
        res = "dataset;nb_elements"
        for scoring_scheme in self.__scoring_schemes:
            res += ";" + scoring_scheme.get_nickname()
        res += "\n"
        flag = [True] * len(self.__scoring_schemes)
        for dataset in sorted(self.datasets, key=lambda dataset_obj: dataset_obj.nb_elements):
            res += dataset.name + ";" + str(dataset.nb_elements)
            id_scoring_scheme = 0
            for scoring_scheme in self.__scoring_schemes:
                if flag[id_scoring_scheme]:
                    time_computation = self.__alg.bench_time_consensus(dataset, scoring_scheme, True)
                    if time_computation > self.__max_time:
                        flag[id_scoring_scheme] = False
                else:
                    time_computation = float('inf')
                res += ";" + str(time_computation)
                id_scoring_scheme += 1
            res += "\n"
        return res

    def _run_final_data(self, raw_data: str) -> str:
        res = "size_datasets"
        for sc in self.__scoring_schemes:
            res += ";"+sc.get_nickname() + "_mean_time"
        res += "\n"
        h_res = {}
        mapping_nb_elements_group = {}
        cpt = 0
        key_mapping = 0
        h_res[0] = {}
        for sc in self.__scoring_schemes:
            h_res[0][sc] = []
        tuples_groups = []
        for i in range(self._dataset_selector.nb_elem_min, self._dataset_selector.nb_elem_max+1):
            cpt += 1
            mapping_nb_elements_group[i] = key_mapping

            if cpt == self.__steps:
                key_mapping += 1
                cpt = 0
                h_res[key_mapping] = {}
                for sc in self.__scoring_schemes:
                    h_res[key_mapping][sc] = []
        for i in range(self._dataset_selector.nb_elem_min, self._dataset_selector.nb_elem_max+1, self.__steps):
            tuples_groups.append((i, i+self.__steps-1))
        for line in raw_data.split("\n")[1:]:
            if len(line) > 1:
                cols = line.split(";")
                nb_elements = int(cols[1])
                col_first_sc = len(cols) - len(self.__scoring_schemes)
                for j in range(col_first_sc, len(cols)):
                    h_res[mapping_nb_elements_group[nb_elements]][self.__scoring_schemes[j-col_first_sc]].append(float(cols[j]))
        for i in range(len(tuples_groups)):
            tuple_i = tuples_groups[i]
            res += str(tuple_i)
            for sc in self.__scoring_schemes:
                res += ";" + str(np.mean(np.asarray(h_res[i][sc])))
            res += "\n"
        return res
#######################################################################################################################


class BenchPartitioningScoringScheme(ExperimentFromDataset):
    def __init__(self,
                 dataset_folder: str,
                 scoring_schemes_exp: List[ScoringScheme],
                 changing_coeff: Tuple[int, int],
                 intervals: List[Tuple[int, int]] = None,
                 dataset_selector_exp: DatasetSelector = None,
                 ):
        super().__init__(dataset_folder, dataset_selector_exp)
        self.__scoring_schemes = scoring_schemes_exp
        self.__alg = get_algorithm(alg=Algorithm.ParCons, parameters={"bound_for_exact": 0,
                                                                      "auxiliary_algorithm":
                                                                          get_algorithm(alg=Algorithm.AllTied)})
        self.__changing_coeff = changing_coeff
        if intervals is not None:
            self.__intervals = intervals
        else:
            max_n = self.datasets[0].nb_elements
            min_n = not self.datasets[0].nb_elements
            for dataset in self.datasets:
                if dataset.nb_elements > max_n:
                    max_n = dataset.nb_elements
                if dataset.nb_elements < min_n:
                    min_n = dataset.nb_elements
            self.__intervals = [(min_n, max_n)]

    def _run_raw_data(self) -> str:
        res = "dataset;nb_elements;"
        for scoring_scheme in self.__scoring_schemes:
            res += str(scoring_scheme.penalty_vectors) + ";"
        res += "\n"
        # for dataset in sorted(self.datasets):
        for dataset in sorted(self.datasets, key=lambda dataset_obj: dataset_obj.nb_elements):
            res += dataset.name + ";" + str(dataset.nb_elements) + ";"
            for scoring_scheme in self.__scoring_schemes:
                consensus = self.__alg.compute_consensus_rankings(dataset, scoring_scheme, True)
                biggest_scc = 0
                for bucket in consensus.consensus_rankings[0]:
                    if len(bucket) > biggest_scc:
                        biggest_scc = len(bucket)
                res += str(biggest_scc) + ";"
            res += "\n"
        return res

    def _run_final_data(self, raw_data: str) -> str:
        mapping_int_interval = {}
        for interval in self.__intervals:
            for i in range(interval[0], interval[1]+1):
                mapping_int_interval[i] = interval
        res = ""
        for scoring_scheme in self.__scoring_schemes:
            value_coeff = scoring_scheme.penalty_vectors[self.__changing_coeff[0]][self.__changing_coeff[1]]
            res += ";" + str(value_coeff)
        res += "\n"
        nb_scoring_schemes = len(self.__scoring_schemes)
        h_res = {}
        for interval in self.__intervals:
            h_res[interval] = {}
            for scoring_scheme in self.__scoring_schemes:
                h_res[interval][scoring_scheme] = []

        for line in raw_data.split("\n")[1:]:
            if len(line) > 1:
                cols = line.split(";")
                id_scoring_scheme = 0
                nb_elem = int(cols[1])
                for i in range(len(cols)-nb_scoring_schemes-1, len(cols)-1):
                    target_value = float(cols[i])
                    h_res[mapping_int_interval[nb_elem]][self.__scoring_schemes[id_scoring_scheme]].append(target_value)
                    id_scoring_scheme += 1

        for interval in self.__intervals:
            res += str(interval)
            for scoring_scheme in self.__scoring_schemes:
                res += ";" + str(round(float(np.mean(np.asarray(h_res[interval][scoring_scheme]))), 2))
            res += "\n"
        return res

#######################################################################################################################
# sc1 = ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)
