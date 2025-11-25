#include "ActionInitialization.hh"

#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "SteppingAction.hh"


namespace BremSim
{
	void ActionInitialization::Build() const{
		
		//Multithread

		// set Geant4 Actions
		SetUserAction(new PrimaryGeneratorAction);
		SetUserAction(new RunAction());
		SetUserAction(new SteppingAction());
	};

	void ActionInitialization::BuildForMaster() const{

		//sequential
		SetUserAction(new RunAction());
	}
}
