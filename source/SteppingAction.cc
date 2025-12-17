#include "SteppingAction.hh"
#include "DetectorConstruction.hh"

#include "G4Step.hh"
#include "G4RunManager.hh"

#include "G4AnalysisManager.hh"
#include "G4RunManager.hh"

#include "G4UnitsTable.hh"
#include "G4ParticleDefinition.hh"


namespace BremSim
{
	SteppingAction::SteppingAction(){}
	
	SteppingAction::~SteppingAction(){}

	void SteppingAction::UserSteppingAction(const G4Step* step)
	{
		// Always update the BremsVolume as it might change between runs (re-initialization)
		const auto detConstruction = static_cast<const DetectorConstruction*>(G4RunManager::GetRunManager()->GetUserDetectorConstruction());
		fBremsVolume = detConstruction->GetBremsVolume();

		G4LogicalVolume* currentVolume =
			step->GetPreStepPoint()->GetTouchableHandle()
			->GetVolume()->GetLogicalVolume();

		if (currentVolume != fBremsVolume){ return; }

		// ntuples for analysis 
		G4int absNTupleID = 0;
		G4int relNTupleID = 1;

		G4int nSecondaryParticles = step->GetNumberOfSecondariesInCurrentStep();
		//if (nSecondaryParticles ==0){ return; }

		// get incident electron energy for recording relative energies
		G4double electronEnergy = step->GetPreStepPoint()->GetKineticEnergy();

		//list seconadry particles 
		const std::vector<const G4Track*>* secondaries = step->GetSecondaryInCurrentStep();

		// Get the analysis manager instance
		auto analysisManager = G4AnalysisManager::Instance();

		//loop through and send the secondary photons to analysisManager
		//for (int i = 0; i < secondaries->size(); i++)
		for (int i = 0; i < 1; i++)
		{
			// tracker to get particle ID
			//const G4Track* track = (*secondaries)[i];
			G4Track* track = step->GetTrack();
			G4String particleName = track->GetParticleDefinition()->GetParticleName();

			// get photons and electrons to analysis Manager
			if (particleName == "gamma" || particleName == "e-" || particleName == "e+")
			{
				static std::map<G4int, G4double> primaryEnergies;

				// Flag to indicate if this is the first step of the track
				G4int eventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();
				G4double initenergy  = step->GetPreStepPoint()->GetKineticEnergy();
				G4double energy = step->GetPostStepPoint()->GetKineticEnergy();
				G4double edep = step->GetTotalEnergyDeposit();
				G4int trackID = track->GetTrackID();
        		G4int parentID = track->GetParentID();
				G4ParticleDefinition* particle = track->GetDefinition();
				G4int pdgCode = particle->GetPDGEncoding();
				G4bool firstStep = false;
				if (primaryEnergies.find(trackID) == primaryEnergies.end()) {
					primaryEnergies[trackID] = step->GetPreStepPoint()->GetKineticEnergy();
					analysisManager->FillNtupleDColumn(absNTupleID, 0, primaryEnergies[trackID]);
					firstStep = true;
				}
				G4int particleID = (particleName == "e-") ? 1 : 0;

				// total energy
				analysisManager->FillNtupleDColumn(absNTupleID, 1, initenergy);
				analysisManager->FillNtupleDColumn(absNTupleID, 2, edep);
				analysisManager->FillNtupleDColumn(absNTupleID, 3, energy);
				//analysisManager->FillNtupleIColumn(absNTupleID, 1, particleID);
				analysisManager->FillNtupleIColumn(absNTupleID, 4, eventID);
				analysisManager->FillNtupleIColumn(absNTupleID, 5, trackID);
				analysisManager->FillNtupleIColumn(absNTupleID, 6, parentID);
				analysisManager->FillNtupleIColumn(absNTupleID, 7, pdgCode);
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