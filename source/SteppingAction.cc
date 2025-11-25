#include "SteppingAction.hh"
#include "DetectorConstruction.hh"

#include "G4Step.hh"
#include "G4RunManager.hh"

#include "G4AnalysisManager.hh"
#include "G4RunManager.hh"

#include "G4UnitsTable.hh"


namespace BremSim
{
	SteppingAction::SteppingAction(){}
	
	SteppingAction::~SteppingAction(){}

	void SteppingAction::UserSteppingAction(const G4Step* step)
	{
		// we want to check if photons are emitted from the Bremsstrahlung emission
		// 1. relative enregy based ont he electron that created it. 
		// 2. total energy spectra of all photons generated
		// Note: if there are other detectors that possible generate secondary photons, they will be recorded a well.

		// first check if we're not in the fBremsVolume
		if(!fBremsVolume)
		{
			const auto detConstruction = static_cast<const DetectorConstruction*>(G4RunManager::GetRunManager()->GetUserDetectorConstruction());
			fBremsVolume = detConstruction->GetBremsVolume();
		}

		G4LogicalVolume* currentVolume =
			step->GetPreStepPoint()->GetTouchableHandle()
			->GetVolume()->GetLogicalVolume();

		if (currentVolume != fBremsVolume){ return; }

		// ntuples for analysis 
		G4int absNTupleID = 0;
		G4int relNTupleID = 1;

		G4int nSecondaryParticles = step->GetNumberOfSecondariesInCurrentStep();
		if (nSecondaryParticles ==0){ return; }

		// get incident electron energy for recording relative energies
		G4double electronEnergy = step->GetPreStepPoint()->GetKineticEnergy();

		//list seconadry particles 
		const std::vector<const G4Track*>* secondaries = step->GetSecondaryInCurrentStep();

		// Get the analysis manager instance
		auto analysisManager = G4AnalysisManager::Instance();

		//loop through and send the secondary photons to analysisManager
		for (int i = 0; i < secondaries->size(); i++)
		{
			// tracker to get particle ID
			const G4Track* track = (*secondaries)[i];
			G4String particleName = track->GetParticleDefinition()->GetParticleName();

			// get photons and electrons to analysis Manager
			if (particleName == "gamma" || particleName == "e-")
			{
				G4double energy = track->GetKineticEnergy();
				G4int particleID = (particleName == "e-") ? 1 : 0;

				// total energy
				analysisManager->FillNtupleDColumn(absNTupleID, 0, energy);
				analysisManager->FillNtupleIColumn(absNTupleID, 1, particleID);
				analysisManager->AddNtupleRow(absNTupleID);

				// relative energy to incident electron
				if (particleName == "gamma") {
					G4double relEnergy = energy/electronEnergy;
					analysisManager->FillNtupleDColumn(relNTupleID, 0, relEnergy);
					analysisManager->AddNtupleRow(relNTupleID);
				}
			}
		}
		
	}
}