from ui.eventmenu import *

from game.game import *
from .styles import STYLES


class BaseMenu(Menu):
    bought_amount_labels = None  # type: typing.Collection[Label]
    budget_label = None  # type: Label

    def __init__(self, window: Window, parent, game: Game, cp: ControlPoint):
        super(BaseMenu, self).__init__(window, parent, game)
        self.cp = cp
        self.base = cp.base
        self.frame = window.right_pane
        self.event = self.game.units_delivery_event(cp)
        self.bought_amount_labels = {}

    def display(self):
        self.window.clear_right_pane()
        row = 0

        def purchase_row(unit_type, unit_price):
            nonlocal row

            existing_units = self.base.total_units_of_type(unit_type)
            scheduled_units = self.event.units.get(unit_type, 0)

            Label(self.frame, text="{}".format(db.unit_type_name(unit_type)), **STYLES["widget"]).grid(row=row, sticky=W)

            label = Label(self.frame, text="({})".format(existing_units), **STYLES["widget"])
            label.grid(column=1, row=row)
            self.bought_amount_labels[unit_type] = label

            Label(self.frame, text="{}m".format(unit_price), **STYLES["widget"]).grid(column=2, row=row, sticky=E)
            Button(self.frame, text="+", command=self.buy(unit_type), **STYLES["btn-primary"]).grid(column=3, row=row, padx=(10,0))
            Button(self.frame, text="-", command=self.sell(unit_type), **STYLES["btn-warning"]).grid(column=4, row=row, padx=(10,5))
            row += 1

        units = {
            PinpointStrike: db.find_unittype(PinpointStrike, self.game.player),
            Embarking: db.find_unittype(Embarking, self.game.player),
            CAS: db.find_unittype(CAS, self.game.player),
            CAP: db.find_unittype(CAP, self.game.player),
            AirDefence: db.find_unittype(AirDefence, self.game.player),
        }

        self.budget_label = Label(self.frame, text="Budget: {}m".format(self.game.budget))
        self.budget_label.grid(row=row, sticky=W)
        Button(self.frame, text="Back", command=self.dismiss, **STYLES["btn-primary"]).grid(column=4, row=row)
        row += 1

        for task_type, units in units.items():
            Label(self.frame, text="{}".format(db.task_name(task_type)), **STYLES["strong"]).grid(row=row, columnspan=5, sticky=NSEW); row += 1

            units = list(set(units))
            units.sort(key=lambda x: db.PRICES[x])
            for unit_type in units:
                purchase_row(unit_type, db.PRICES[unit_type])

    def dismiss(self):
        if sum([x for x in self.event.units.values()]) == 0:
            self.game.units_delivery_remove(self.event)

        super(BaseMenu, self).dismiss()

    def _update_count_label(self, unit_type: UnitType):
        self.bought_amount_labels[unit_type]["text"] = "({}{})".format(
            self.cp.base.total_units_of_type(unit_type),
            unit_type in self.event.units and ", bought {}".format(self.event.units[unit_type]) or ""
        )

        self.budget_label["text"] = "Budget: {}m".format(self.game.budget)

    def buy(self, unit_type):
        def action():
            price = db.PRICES[unit_type]
            if self.game.budget >= price:
                self.event.deliver({unit_type: 1})
                self.game.budget -= price

            self._update_count_label(unit_type)

        return action

    def sell(self, unit_type):
        def action():
            if self.event.units.get(unit_type, 0) > 0:
                price = db.PRICES[unit_type]
                self.game.budget += price
                self.event.units[unit_type] = self.event.units[unit_type] - 1
                if self.event.units[unit_type] == 0:
                    del self.event.units[unit_type]
            elif self.base.total_units_of_type(unit_type) > 0:
                price = db.PRICES[unit_type]
                self.game.budget += price
                self.base.commit_losses({unit_type: 1})

            self._update_count_label(unit_type)

        return action