package gwfs.pages;

import org.apache.tapestry5.util.TextStreamResponse;

public class HelloWorldStatic {
    /**
     * The activate event is fired on the Tapestry page instance early in the request cycle. Normally, it's job is to set up the state of the page, prior to
     * processing the request (or rendering the template), and it returns void. Here we're bending things a lot ... bypassing the template part of Tapestry to return
     * a fixed string response, a very rarely used option in Tapestry.
     */
    Object onActivate() {
        return new TextStreamResponse("text/html", "    <p>Lorem ipsum dolor sit amet, consecteteur adipiscing elit nisi ultricies. Condimentum vel, at augue nibh sed. Diam praesent metus ut eros, " +
                "sem penatibus. Pellentesque. Fusce odio posuere litora non integer habitant proin. Metus accumsan nibh facilisis nostra lobortis cum diam tellus. " +
                "Malesuada nostra a volutpat pede primis congue nisl feugiat in fermentum. Orci in hymenaeos. Eni tempus mi mollis lacinia orci interdum lacus. " +
                "Sollicitudin aliquet, etiam. Ac. Mi, nullam ligula, tristique penatibus nisi eros nisl pede pharetra congue, aptent nulla, rhoncus tellus morbi, ornare. " +
                "Magna condimentum erat turpis. Fusce arcu ve suscipit nisi phasellus rutrum a dictumst leo, laoreet dui, ultricies platea. Porta venenatis fringilla vestibulum arcu etiam condimentum non.</p>\n");
    }
}
