#ifndef BREMSIM_PHYSICSLIST_H
#define BREMSIM_PHYSICSLIST_H 1

#include "G4VModularPhysicsList.hh"


namespace BremSim
{
	class PhysicsList : public G4VModularPhysicsList
	{
		public:
			PhysicsList();
			virtual ~PhysicsList() override = default;

			// mandatory methods to override
			virtual void ConstructParticle() override;
			virtual void ConstructProcess() override;
			virtual void SetCuts() override;
			
	};
}
#endif
