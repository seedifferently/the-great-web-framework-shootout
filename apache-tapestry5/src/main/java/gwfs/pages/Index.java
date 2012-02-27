package gwfs.pages;

import org.apache.tapestry5.SymbolConstants;
import org.apache.tapestry5.alerts.AlertManager;
import org.apache.tapestry5.annotations.InjectComponent;
import org.apache.tapestry5.annotations.Persist;
import org.apache.tapestry5.annotations.Property;
import org.apache.tapestry5.corelib.components.Zone;
import org.apache.tapestry5.ioc.annotations.Inject;
import org.apache.tapestry5.ioc.annotations.Symbol;

import java.util.Date;

/**
 * Start page of application t5app.
 */
public class Index {
    @Property
    @Inject
    @Symbol(SymbolConstants.TAPESTRY_VERSION)
    private String tapestryVersion;

    @InjectComponent
    private Zone zone;

    @Persist
    @Property
    private int clickCount;

    @Inject
    private AlertManager alertManager;

    public Date getCurrentTime() {
        return new Date();
    }

    void onActionFromIncrement() {
        alertManager.info("Increment clicked");

        clickCount++;
    }

    Object onActionFromIncrementAjax() {
        clickCount++;

        alertManager.info("Increment (via Ajax) clicked");

        return zone;
    }
}
