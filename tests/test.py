import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from csc import csc_matvec, dense_to_csc
from csr import csr_matvec, dense_to_csr
from data_generator import generate_matrix
from dense import dense_matvec


class MatrixOperationsTests(unittest.TestCase):
    def test_all_python_sources_compile(self):
        source_files = sorted(SRC_DIR.glob("*.py"))
        self.assertTrue(source_files, "No Python source files found in src/")

        for source_file in source_files:
            with self.subTest(source=source_file.name):
                compile(
                    source_file.read_text(encoding="utf-8"),
                    str(source_file),
                    "exec",
                )

    def test_dense_csr_and_csc_matvec_on_rectangular_matrix(self):
        matrix = [
            [1.0, 0.0, 2.0, 0.0],
            [0.0, 3.0, 0.0, 4.0],
            [5.0, 0.0, 0.0, 6.0],
        ]
        vector = [2.0, 3.0, 4.0, 5.0]
        expected = [10.0, 29.0, 40.0]

        self.assertEqual(dense_matvec(matrix, vector), expected)

        csr_data, csr_indices, csr_indptr = dense_to_csr(matrix)
        self.assertEqual(
            csr_matvec(csr_data, csr_indices, csr_indptr, vector),
            expected,
        )

        csc_data, csc_indices, csc_indptr = dense_to_csc(matrix)
        self.assertEqual(
            csc_matvec(
                csc_data,
                csc_indices,
                csc_indptr,
                vector,
                len(matrix),
            ),
            expected,
        )

    def test_sparse_formats_handle_all_zero_matrix(self):
        matrix = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        vector = [1.0, 2.0, 3.0]

        csr_data, csr_indices, csr_indptr = dense_to_csr(matrix)
        self.assertEqual(csr_data, [])
        self.assertEqual(
            csr_matvec(csr_data, csr_indices, csr_indptr, vector),
            [0.0, 0.0],
        )

        csc_data, csc_indices, csc_indptr = dense_to_csc(matrix)
        self.assertEqual(csc_data, [])
        self.assertEqual(
            csc_matvec(
                csc_data,
                csc_indices,
                csc_indptr,
                vector,
                len(matrix),
            ),
            [0.0, 0.0],
        )

    def test_matrix_generator_is_deterministic_and_has_requested_nnz(self):
        for structure in ("random", "banded", "row", "block"):
            with self.subTest(structure=structure):
                matrix = generate_matrix(
                    3, 5, 0.4, seed=42, structure=structure
                )
                repeated = generate_matrix(
                    3, 5, 0.4, seed=42, structure=structure
                )
                nnz = sum(value != 0 for row in matrix for value in row)

                self.assertEqual(matrix, repeated)
                self.assertEqual(nnz, 6)

    def test_matrix_generator_rejects_invalid_input(self):
        with self.assertRaises(ValueError):
            generate_matrix(0, 5, 0.4)

        with self.assertRaises(ValueError):
            generate_matrix(3, 5, 1.1)

        with self.assertRaises(ValueError):
            generate_matrix(3, 5, 0.4, structure="unknown")


if __name__ == "__main__":
    unittest.main()
