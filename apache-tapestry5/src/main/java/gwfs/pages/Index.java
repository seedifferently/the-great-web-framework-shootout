package gwfs.pages;

import org.apache.tapestry5.util.TextStreamResponse;

/**
 * Start page of application t5app.
 */
public class Index {

    /**
     * This a component action event handler method, for the implicit 'action' event from the "text" ActionLink component in the template.
     * Normally, this would perform an operation and indicate which page renders the response (which would also, normally, involve
     * a client-side redirect); we're using a rarely-used Tapestry option to directly return a String as the response.
     */
    Object onActionFromText() {
        return new TextStreamResponse("text/plain", "Hello World!");
    }
}
