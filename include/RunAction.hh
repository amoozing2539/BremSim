#ifndef BREMSIM_RUNACTION_HH
#define BREMSIM_RUNACTION_HH

#include "G4UserRunAction.hh"
#include "globals.hh"
#include "G4AnalysisManager.hh"

// time the run
#include "G4Timer.hh"


namespace BremSim
{

	class HitsCollection;
	
	class RunAction : public G4UserRunAction
	{
		public:
			RunAction();
			~RunAction();

			void BeginOfRunAction(const G4Run* aRun) override;
			void EndOfRunAction(const G4Run* aRun) override;
		
		private:
			// just want to save the amount of time per action
			G4Timer fTimer;
			void PrintTime();
	};
}
#endif