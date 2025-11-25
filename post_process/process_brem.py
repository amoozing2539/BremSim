import os
import sys
import logging
import uproot
import pandas as pd
import matplotlib.pyplot as plt


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# Path to the ROOT file (adjust if needed)
file_path = "C:\\Geant4_Projects\\BremSim\\build\\Release\\output.root"


def find_tree_name(root_file):
	"""Return a likely tree name from an opened uproot file.

	Prefers objects whose classname contains 'TTree'. Falls back to the
	first available key if no TTree is found.
	"""
	try:
		classnames = root_file.classnames()
	except Exception:
		# older/newer uproot versions may behave slightly differently
		classnames = {k: str(root_file[k].classname) for k in root_file.keys()}

	if not classnames:
		return None

	for name, cls in classnames.items():
		# classname may be bytes; coerce to str
		cls_str = cls.decode() if isinstance(cls, (bytes, bytearray)) else str(cls)
		if "TTree" in cls_str or "TNtuple" in cls_str or "RNTuple" in cls_str:
			return name

	# fallback: return the first key
	return next(iter(classnames.keys()))


def flatten_multiindex_columns(df: pd.DataFrame) -> pd.DataFrame:
	if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
		df = df.copy()
		df.columns = ["_".join(map(str, col)).strip("_") for col in df.columns.values]
	return df


def process_root(file_path: str) -> pd.DataFrame:
	if not os.path.exists(file_path):
		logging.error("ROOT file not found: %s", file_path)
		raise FileNotFoundError(file_path)

	logging.info("Opening ROOT file: %s", file_path)
	try:
		root_file = uproot.open(file_path)
	except Exception as e:
		logging.exception("Failed to open ROOT file: %s", e)
		raise

	# Specific tree name for BremSim
	tree_name = "Absolute Energies"
	logging.info("Using tree/key: %s", tree_name)

	try:
		tree = root_file[tree_name]
	except Exception as e:
		logging.exception("Failed to retrieve tree '%s': %s", tree_name, e)
		raise

	# If tree reports 0 entries, bail out early with a helpful message
	num_entries = None
	try:
		num_entries = getattr(tree, "num_entries", None)
		if num_entries is None:
			# fallback: try len on the first branch
			branches = list(tree.keys()) if hasattr(tree, "keys") else []
			if branches:
				arr = tree[branches[0]].array()
				num_entries = len(arr)
	except Exception:
		num_entries = None

	if num_entries == 0:
		logging.error("Tree '%s' exists but has 0 entries.", tree_name)
		raise RuntimeError("Empty tree: 0 entries")

	logging.info("Converting tree to pandas DataFrame (this may take a moment)...")
	try:
		df = tree.arrays(library="pd")
	except Exception:
		logging.exception("Failed to convert tree arrays to DataFrame.")
		# Provide some debugging info about available branches
		try:
			logging.info("Available branches/keys: %s", list(tree.keys()))
		except Exception:
			pass
		raise

	df = flatten_multiindex_columns(df)

	logging.info("DataFrame shape: %s", df.shape)
	return df


if __name__ == "__main__":
	try:
		df = process_root(file_path)
	except Exception as e:
		logging.error("Processing failed: %s", e)
		sys.exit(1)

	# Show a quick preview
	logging.info("First few rows:\n%s", df.head())

	# Save a CSV alongside the ROOT file for downstream analysis
	csv_path = os.path.splitext(file_path)[0] + "_dataset.csv"
	pkl_path = os.path.splitext(file_path)[0] + "_dataset.pkl"
	try:
		df.to_csv(csv_path, index=False)
		df.to_pickle(pkl_path)
		logging.info("Saved dataset CSV to: %s", csv_path)
		logging.info("Saved dataset PKL to: %s", pkl_path)
	except Exception:
		logging.exception("Failed to save DataFrame to CSV/PKL")

	# Plotting
	if "AbsEnergy" in df.columns:
		plt.figure(figsize=(10, 6))
		
		# Check if ParticleID exists
		if "ParticleID" in df.columns:
			# Photons (ParticleID == 0)
			photons = df[df["ParticleID"] == 0]["AbsEnergy"]
			# Electrons (ParticleID == 1)
			electrons = df[df["ParticleID"] == 1]["AbsEnergy"]
			
			plt.hist(photons, bins=100, log=True, histtype='stepfilled', alpha=0.5, label='Photons', color='blue')
			plt.hist(electrons, bins=100, log=True, histtype='stepfilled', alpha=0.5, label='Electrons', color='red')
			plt.legend()
		else:
			# Fallback if no ParticleID
			plt.hist(df["AbsEnergy"], bins=100, log=True, histtype='stepfilled', alpha=0.7, label='All Particles')
			
		plt.title("Particle Energy Spectrum")
		plt.xlabel("Energy (MeV)")
		plt.ylabel("Counts")
		plt.grid(True, which="both", ls="--", alpha=0.5)
		
		plot_path = os.path.join(os.path.dirname(file_path), "particle_spectrum.png")
		local_plot_path = os.path.join(os.path.dirname(__file__), "particle_spectrum.png")
		
		try:
			plt.savefig(local_plot_path)
			logging.info("Saved plot to: %s", local_plot_path)
		except Exception:
			logging.exception("Failed to save plot to: %s", local_plot_path)
	else:
		logging.warning("'AbsEnergy' column not found in DataFrame. Skipping plot.")