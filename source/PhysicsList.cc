#include "PhysicsList.hh"

#include "G4EmStandardPhysics.hh"
#include "G4LossTableManager.hh"
#include "G4EmLivermorePhysics.hh"
#include "G4EmPenelopePhysics.hh"

// Different options to test
#include "G4EmStandardPhysics_option1.hh"
#include "G4EmStandardPhysics_option2.hh"
#include "G4EmStandardPhysics_option3.hh"
#include "G4EmStandardPhysics_option4.hh"
#include "G4EmStandardPhysicsWVI.hh"
#include "G4EmStandardPhysicsSS.hh"
#include "G4EmStandardPhysicsGS.hh"


namespace BremSim
{
	PhysicsList::PhysicsList() : G4VModularPhysicsList()
	{
		// Register the high-accuracy EM physics package (accurate electron bremmstrahlung and photon interaction)
		RegisterPhysics(new G4EmStandardPhysics());
	}

	void PhysicsList::ConstructParticle()
	{
		G4VModularPhysicsList::ConstructParticle();
	}

	void PhysicsList::ConstructProcess()
	{
		G4VModularPhysicsList::ConstructProcess();
	}
}
