#include "ActionInitialization.hh"

#include "EventAction.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "SteppingAction.hh"


namespace BremSim
{
	void ActionInitialization::Build() const{
		
		//Multithread

		// set Geant4 Actions
		SetUserAction(new PrimaryGeneratorAction);
		SetUserAction(new Runaction());
		SetUserAction(new SteppingAction());
	};

	void ActionInitialization::BuildForMaster() const{

		//sequential
		SetUserAction(newRunAction());
	}
}
