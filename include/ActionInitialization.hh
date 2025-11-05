#ifndef BremSim_ActionInitialization_H
#define BremSim_ActionInitialization_H 1

#include "G4VUserActionInitialization.hh"

namespace BremSim
{
	class ActionInitialization: public G4VUserActionInitialization
	{
		public:
			ActionInitialization() = default;
			~ActionInitialization() override = default;

			void Build() const override;
			void BuildForMaster() const override;
	};
}

#endif