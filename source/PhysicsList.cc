#include "PhysicsList.hh"
#include "G4EmStandardPhysics_option4.hh"

PhysicsList::PhysicsList() : G4VModularPhysicsList()
{
	// Register the high-accuracy electromagnetic physics package (accurate electron bremmstrahlung and photon interactions)
	RegisterPhysics(new G4EmStandardPhysics_option4());
}

PhysicsList::~PhysicsList() {}