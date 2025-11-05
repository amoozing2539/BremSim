#ifndef BREMSIM_RUNACTION_HH
#define BREMSIM_RUNACTION_HH

#include "G4UserRunAction.hh"
#include "globals.hh"
#include "G4AnalysisManager"

// time the run
#include "G4Timer.hh"

namespace BremSim
{

	class HitsCollection;
	
	class RunAction : public G4UserrunAction
	{
		public:
			RunAction();
			~RunAction();

			void BegOfRunAction(const G4Run* aRun) override;
			void EndOfRunAction(const G4Run* aRun) override;
		
		private:

			G4timer fTimer;
			void PrintTime();
	};
}
#endif