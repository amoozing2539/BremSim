#include "RunAction.hh"
#include "G4ThreeVector.hh"
#include "G4UnitsTable.hh"


namespace BremSim
{
	RunAction::RunAction()
	{
		// set up analysis nTuples and output files

		auto analysisManager = G4AnalysisManager::Instance();

		// set default settings
		analysisManager->SetDefaultFileType("root");
		analysisManager->SetNtupleMerging(true);
		analysisManager->SetVerboseLevel(1);
		analysisManager->SetFileName("output");

		// create nTuple to store the absolute energies
		const G4int ntupleID1 = analysisManager->CreateNtuple("Absolute Energies", "Gamma Energies");
		analysisManager->CreateNtupleDColumn(ntupleID1, "AbsEnergy");
		analysisManager->FinishNtuple(ntupleID1);

		// create nTuple for the relative energies
		const G4int ntupleId2 = analysisManager->CreateNtuple("Relative Energies", "Gamma Energies");
		analysisManager->CreateNtupleDColumn(ntupleId2, "RelEnergy");
		analysisManager->FinishNtuple(ntupleId2);
	}


	RunAction::~RunAction()
	{

	}


	void RunAction::BeginOfRunAction(const G4Run* run)
	{
		// start time 
		fTimer.Start();

		auto analysisManager = G4AnalysisManager::Instance();

		// open the file at the start of the run
		analysisManager->OpenFile();
	}


	void RunAction::EndOfRunAction(const G4Run* run)
	{
		auto analysisManager = G4AnalysisManager::Instance();

		// write to output file 
		analysisManager->Write();
		analysisManager->CloseFile();

		// end time
		fTimer.Stop();

		// print out the time it took 
		if(IsMaster()){ PrintTime(); }
	}


	void RunAction::PrintTime()
	{
		auto time = fTimer.GetRealElapsed();

		G4cout 
			<< "Elapsed time: "
			<< time
			<< " Seconds."
			<< G4endl;
	}
}