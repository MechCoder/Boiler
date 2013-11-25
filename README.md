Boiler
======

A python repository to simulate a boiler with a few accessories. This
has been prepared in partial fulfillment of ME F266 course.
Accessories that have been added included

1] Feed Pump

2] Economiser

3] Air Preheater

4] Superheater

A simple example

    boil = Boiler(300)

    boil.feed_pump(400)

    boil.economiser(400, 300)

    boil.boiler()

    boil.effectiveness()

    0.08965779091595147

    boil.actual_heat()

    2055.4663531119345


Efficiency can also be added.
